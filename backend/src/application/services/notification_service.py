"""
Notification Service

Orquestrador central do sistema de notificações.
Responsável por coordenar persistência, envio real-time (WebSocket) e push notifications.
"""

import structlog
from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.notification_dtos import NotificationResponseDTO
from src.domain.entities.notification import (
    Notification,
    NotificationActionType,
    NotificationType,
)
from src.domain.interfaces.notification_repository import INotificationRepository
from src.domain.interfaces.push_notification_service import IPushNotificationService
from src.interface.websockets.connection_manager import ConnectionManager

logger = structlog.get_logger()


@dataclass
class NotificationService:
    """
    Orquestrador central do sistema de notificações.

    Pipeline de envio:
        1. Persiste a notificação no banco de dados (sempre).
        2. Envia via WebSocket em tempo real (se o usuário está online).
        3. Envia push notification (apenas se o usuário está offline).

    A persistência é garantida independentemente do canal de entrega,
    assegurando que o histórico no sininho seja completo.
    """

    notification_repository: INotificationRepository
    push_service: IPushNotificationService
    ws_manager: ConnectionManager

    # =========================================================================
    # Envio de notificações
    # =========================================================================

    async def notify(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        action_type: NotificationActionType | None = None,
        action_id: UUID | None = None,
    ) -> Notification:
        """
        Envia uma notificação para um usuário pelos canais disponíveis.

        Args:
            user_id: ID do usuário destinatário.
            notification_type: Tipo da notificação.
            title: Título exibido na notificação.
            body: Corpo da mensagem.
            action_type: Tipo do destino do deep link (SCHEDULING, CHAT, etc.).
            action_id: ID do recurso de destino.

        Returns:
            Notificação persistida.
        """
        # 1. Persistir no banco (sempre)
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            action_type=action_type,
            action_id=action_id,
        )
        saved = await self.notification_repository.create(notification)

        logger.info(
            "notification_created",
            notification_id=str(saved.id),
            user_id=str(user_id),
            type=notification_type.value,
        )

        # 2. Enviar via WebSocket se o usuário estiver online
        if self.ws_manager.is_online(user_id):
            from src.application.dtos.notification_dtos import NotificationSchema
            unread_count = await self.notification_repository.count_unread(user_id)
            notification_dto = _to_response_dto(saved)
            notification_dict = NotificationSchema.model_validate(notification_dto).model_dump(mode="json")
            await self.ws_manager.send_to_user(
                user_id,
                {
                    "type": "NOTIFICATION",
                    "payload": {
                        "notification": notification_dict,
                        "unread_count": unread_count,
                    },
                },
            )
            logger.info("notification_sent_websocket", user_id=str(user_id))
        else:
            # 3. Enviar push notification se o usuário estiver offline
            push_data = {
                "type": notification_type.value,
                "action_type": action_type.value if action_type else None,
                "action_id": str(action_id) if action_id else None,
            }
            await self.push_service.send_to_user(
                user_id=user_id,
                title=title,
                body=body,
                data=push_data,
            )

        return saved

    # =========================================================================
    # Leitura de notificações (para endpoints REST)
    # =========================================================================

    async def get_notifications(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """
        Retorna notificações do usuário paginadas, mais recentes primeiro.

        Args:
            user_id: UUID do usuário.
            limit: Quantidade máxima a retornar.
            offset: Posição inicial para paginação.

        Returns:
            Lista de notificações ordenada por data desc.
        """
        return await self.notification_repository.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    async def get_unread_count(self, user_id: UUID) -> int:
        """
        Retorna a contagem de notificações não lidas do usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Quantidade de notificações não lidas.
        """
        return await self.notification_repository.count_unread(user_id)

    # =========================================================================
    # Ações sobre notificações
    # =========================================================================

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """
        Marca uma notificação específica como lida.

        Args:
            notification_id: UUID da notificação.
            user_id: UUID do proprietário (proteção contra acesso não autorizado).

        Returns:
            True se atualizado com sucesso, False se não encontrado/já lido.
        """
        return await self.notification_repository.mark_as_read(
            notification_id=notification_id,
            user_id=user_id,
        )

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas as notificações não lidas do usuário como lidas.

        Args:
            user_id: UUID do usuário.

        Returns:
            Quantidade de notificações atualizadas.
        """
        return await self.notification_repository.mark_all_as_read(user_id)

    async def delete_read_notifications(self, user_id: UUID) -> int:
        """
        Exclui todas as notificações já lidas do usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Quantidade de notificações excluídas.
        """
        count = await self.notification_repository.delete_read_notifications(user_id)
        logger.info("read_notifications_deleted", user_id=str(user_id), count=count)
        return count

    # =========================================================================
    # Gerenciamento de Push Tokens
    # =========================================================================

    async def register_push_token(
        self,
        user_id: UUID,
        token: str,
        device_id: str | None = None,
        platform: str | None = None,
    ) -> None:
        """
        Registra ou reativa um Expo Push Token do dispositivo.

        Deve ser chamado ao fazer login ou quando o token é renovado.

        Args:
            user_id: UUID do usuário dono do dispositivo.
            token: Expo Push Token.
            device_id: Identificador do dispositivo (opcional).
            platform: Plataforma ('ios' | 'android').
        """
        await self.push_service.register_token(
            user_id=user_id,
            token=token,
            device_id=device_id,
            platform=platform,
        )
        logger.info(
            "push_token_registered",
            user_id=str(user_id),
            platform=platform,
        )

    async def unregister_push_token(self, user_id: UUID, token: str) -> bool:
        """
        Remove um Expo Push Token (chamado no logout ou desinstalação).

        Args:
            user_id: UUID do proprietário do token.
            token: Expo Push Token a remover.

        Returns:
            True se removido com sucesso, False se não encontrado.
        """
        try:
            await self.push_service.unregister_token(token=token, user_id=user_id)
            logger.info("push_token_unregistered", user_id=str(user_id))
            return True
        except Exception:
            return False


def _to_response_dto(notification: Notification) -> NotificationResponseDTO:
    """Converte entidade de domínio para DTO de resposta."""
    return NotificationResponseDTO(
        id=notification.id,
        type=notification.type.value,
        title=notification.title,
        body=notification.body,
        action_type=notification.action_type.value if notification.action_type else None,
        action_id=notification.action_id,
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )
