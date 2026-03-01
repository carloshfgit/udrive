"""
Expo Push Notification Service

Serviço concreto de push notifications via Expo Push API.
Implementa IPushNotificationService e gerencia push tokens no banco.
"""

import structlog
from uuid import UUID

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.push_notification_service import IPushNotificationService
from src.infrastructure.db.models.push_token_model import PushTokenModel
from src.infrastructure.repositories.push_token_repository_impl import (
    PushTokenRepositoryImpl,
)

logger = structlog.get_logger()

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


class ExpoPushNotificationService(IPushNotificationService):
    """
    Implementação concreta do IPushNotificationService via Expo Push API.

    Responsabilidades:
    - Registrar/remover tokens de dispositivo via PushTokenRepository
    - Buscar tokens ativos do usuário no banco
    - Enviar notificações para todos os dispositivos simultaneamente
    - Processar recibos e desativar tokens inválidos (DeviceNotRegistered)
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._token_repo = PushTokenRepositoryImpl(session)

    async def send_to_user(
        self,
        user_id: UUID,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        """
        Envia push notification para todos os dispositivos ativos do usuário.

        Se não há tokens ativos, retorna silenciosamente.
        Tokens inválidos são desativados automaticamente após a resposta.

        Args:
            user_id: UUID do usuário destinatário.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Payload adicional (deep link type, action_id, etc.).
        """
        tokens = await self._token_repo.get_active_tokens_by_user(user_id)
        if not tokens:
            logger.info("push_no_tokens", user_id=str(user_id))
            return

        messages = [
            {
                "to": token,
                "title": title,
                "body": body,
                "data": data or {},
                "sound": "default",
                "priority": "high",
                "channelId": "default",
            }
            for token in tokens
        ]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    EXPO_PUSH_URL,
                    json=messages,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            if response.status_code != 200:
                logger.error(
                    "push_send_failed",
                    status=response.status_code,
                    user_id=str(user_id),
                )
                return

            await self._handle_receipts(response.json(), tokens)

        except httpx.TimeoutException:
            logger.error("push_send_timeout", user_id=str(user_id))
        except Exception as exc:
            logger.error(
                "push_send_error",
                user_id=str(user_id),
                error=str(exc),
            )

    async def register_token(
        self,
        user_id: UUID,
        token: str,
        device_id: str | None = None,
        platform: str | None = None,
    ) -> None:
        """
        Registra ou reativa o push token de um dispositivo.

        Args:
            user_id: UUID do usuário dono do dispositivo.
            token: Expo Push Token.
            device_id: Identificador do dispositivo (opcional).
            platform: Plataforma ('ios' | 'android').
        """
        await self._token_repo.create_or_update(
            user_id=user_id,
            token=token,
            device_id=device_id,
            platform=platform,
        )

    async def unregister_token(self, token: str, user_id: UUID) -> None:
        """
        Remove um push token (logout ou desinstalação).

        Args:
            token: Expo Push Token a remover.
            user_id: UUID do proprietário (validação de ownership).
        """
        await self._token_repo.delete_token(token=token, user_id=user_id)

    async def _handle_receipts(
        self, response_data: dict, tokens: list[str]
    ) -> None:
        """
        Processa recibos da API Expo e desativa tokens inválidos.

        Um token é desativado quando o Expo reporta `DeviceNotRegistered`,
        indicando que o app foi desinstalado ou o token expirou.

        Args:
            response_data: Resposta JSON da API Expo.
            tokens: Lista de tokens na mesma ordem dos tickets.
        """
        tickets = response_data.get("data", [])
        for i, ticket in enumerate(tickets):
            if ticket.get("status") == "error":
                error_type = ticket.get("details", {}).get("error", "")
                if error_type == "DeviceNotRegistered" and i < len(tokens):
                    await self._token_repo.deactivate_token(tokens[i])
                    logger.info(
                        "push_token_deactivated",
                        token=tokens[i][:20] + "...",
                    )
