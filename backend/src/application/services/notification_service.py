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
            unread_count = await self.notification_repository.count_unread(user_id)
            await self.ws_manager.send_to_user(
                user_id,
                {
                    "type": "NOTIFICATION",
                    "payload": {
                        "notification": _to_response_dto(saved).__dict__,
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
