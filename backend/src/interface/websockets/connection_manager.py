"""
WebSocket Connection Manager

Gerencia conexões WebSocket ativas em memória.
Suporta múltiplas conexões por usuário (multi-device).
"""

import structlog
from uuid import UUID

from fastapi import WebSocket

logger = structlog.get_logger()


class ConnectionManager:
    """
    Gerencia conexões WebSocket ativas em memória.

    Cada usuário pode ter múltiplas conexões simultâneas (ex: celular + tablet).
    Limite configurável via `max_connections_per_user`.
    """

    def __init__(self, max_connections_per_user: int = 5) -> None:
        self._active_connections: dict[UUID, list[WebSocket]] = {}
        self._max_connections_per_user = max_connections_per_user

    async def connect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Aceita e registra uma nova conexão WebSocket.

        Se o usuário já atingiu o limite de conexões simultâneas,
        a conexão mais antiga é desconectada.

        Args:
            user_id: UUID do usuário.
            websocket: Instância do WebSocket.
        """
        await websocket.accept()

        if user_id not in self._active_connections:
            self._active_connections[user_id] = []

        connections = self._active_connections[user_id]

        # Se atingiu o limite, desconectar a conexão mais antiga
        if len(connections) >= self._max_connections_per_user:
            oldest = connections.pop(0)
            try:
                await oldest.close(code=1000, reason="Limite de conexões atingido")
            except Exception:
                pass  # Conexão pode já estar fechada

        connections.append(websocket)

        logger.info(
            "websocket_connected",
            user_id=str(user_id),
            total_connections=len(connections),
        )

    async def disconnect(self, user_id: UUID, websocket: WebSocket) -> None:
        """
        Remove uma conexão WebSocket.

        Args:
            user_id: UUID do usuário.
            websocket: Instância do WebSocket a remover.
        """
        if user_id in self._active_connections:
            connections = self._active_connections[user_id]
            if websocket in connections:
                connections.remove(websocket)
            if not connections:
                del self._active_connections[user_id]

        logger.info(
            "websocket_disconnected",
            user_id=str(user_id),
            remaining_connections=len(self._active_connections.get(user_id, [])),
        )

    async def send_to_user(self, user_id: UUID, data: dict) -> None:
        """
        Envia dados JSON para todas as conexões ativas de um usuário.

        Conexões inválidas são removidas automaticamente.

        Args:
            user_id: UUID do destinatário.
            data: Dicionário a ser serializado como JSON.
        """
        if user_id not in self._active_connections:
            return

        connections = self._active_connections[user_id]
        dead_connections: list[WebSocket] = []

        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead_connections.append(ws)
                logger.warning(
                    "websocket_send_failed",
                    user_id=str(user_id),
                )

        # Limpar conexões mortas
        for ws in dead_connections:
            if ws in connections:
                connections.remove(ws)
        if not connections:
            del self._active_connections[user_id]

    def is_online(self, user_id: UUID) -> bool:
        """
        Verifica se o usuário possui conexões WebSocket ativas.

        Args:
            user_id: UUID do usuário.

        Returns:
            True se o usuário está online.
        """
        return user_id in self._active_connections and len(self._active_connections[user_id]) > 0

    @property
    def active_user_count(self) -> int:
        """Retorna o número de usuários com conexões ativas."""
        return len(self._active_connections)


# Instância global (singleton)
manager = ConnectionManager()
