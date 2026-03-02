"""
Chat Notification Decorators

Decorator que envolve o SendMessageUseCase e dispara notificação
para o destinatário da mensagem após envio bem-sucedido.
"""

import structlog
from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.chat_dtos import MessageResponseDTO, SendMessageDTO
from src.application.services.notification_service import NotificationService
from src.application.use_cases.chat.send_message_use_case import SendMessageUseCase
from src.domain.entities.notification import NotificationActionType, NotificationType

logger = structlog.get_logger()


@dataclass
class NotifyOnSendMessage:
    """
    Decorator de SendMessageUseCase.

    Após envio bem-sucedido de mensagem, notifica o destinatário com
    NEW_CHAT_MESSAGE para garantir histórico no sininho e push quando offline.

    Nota: o chat já possui canal WebSocket próprio para entrega real-time da
    mensagem em si; esta notificação serve para o badge do sininho e push
    quando o destinatário estiver offline.
    """

    _wrapped: SendMessageUseCase
    _notification_service: NotificationService

    async def execute(self, sender_id: UUID, dto: SendMessageDTO) -> MessageResponseDTO:
        result = await self._wrapped.execute(sender_id, dto)

        try:
            # Buscar o nome do remetente para mensagem mais amigável
            sender = await self._wrapped.user_repository.get_by_id(sender_id)
            sender_name = sender.full_name if sender else "Alguém"

            # Preview do conteúdo (truncado para não expor a mensagem completa)
            preview = dto.content[:50] + "..." if len(dto.content) > 50 else dto.content

            await self._notification_service.notify(
                user_id=dto.receiver_id,
                notification_type=NotificationType.NEW_CHAT_MESSAGE,
                title=f"Nova mensagem de {sender_name} 💬",
                body=preview,
                action_type=NotificationActionType.CHAT,
                action_id=sender_id,  # action_id = sender → app abre o chat com esse usuário
            )
        except Exception:
            logger.exception(
                "notify_on_send_message_failed",
                sender_id=str(sender_id),
                receiver_id=str(dto.receiver_id),
            )

        return result
