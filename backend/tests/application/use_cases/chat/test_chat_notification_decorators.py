"""
Testes unitários para o Chat Notification Decorator.

Verifica que NotifyOnSendMessage:
1. Delega ao SendMessageUseCase encapsulado
2. Notifica o destinatário com NEW_CHAT_MESSAGE
3. Não bloqueia o fluxo se notify() falhar
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.chat_dtos import MessageResponseDTO, SendMessageDTO
from src.application.use_cases.chat.chat_notification_decorators import NotifyOnSendMessage
from src.domain.entities.notification import NotificationActionType, NotificationType


def make_message_response(sender_id=None, receiver_id=None) -> MessageResponseDTO:
    from datetime import datetime, timezone
    return MessageResponseDTO(
        id=uuid4(),
        sender_id=sender_id or uuid4(),
        receiver_id=receiver_id or uuid4(),
        content="Olá, como vai?",
        timestamp=datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc),
        is_read=False,
    )


class TestNotifyOnSendMessage:
    @pytest.mark.asyncio
    async def test_notifies_receiver_with_new_chat_message(self):
        """Deve notificar o destinatário com NEW_CHAT_MESSAGE após envio."""
        sender_id = uuid4()
        receiver_id = uuid4()
        result = make_message_response(sender_id=sender_id, receiver_id=receiver_id)

        # Mock do SendMessageUseCase
        wrapped = MagicMock()
        wrapped.execute = AsyncMock(return_value=result)

        # Mock do user_repository para buscar nome do remetente
        sender_user = MagicMock()
        sender_user.full_name = "Carlos Aluno"
        wrapped.user_repository = AsyncMock()
        wrapped.user_repository.get_by_id = AsyncMock(return_value=sender_user)

        notification_svc = AsyncMock()

        dto = SendMessageDTO(receiver_id=receiver_id, content="Olá, como vai?")
        decorator = NotifyOnSendMessage(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        returned = await decorator.execute(sender_id, dto)

        assert returned == result
        notification_svc.notify.assert_awaited_once()
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == receiver_id
        assert call_kwargs["notification_type"] == NotificationType.NEW_CHAT_MESSAGE
        assert call_kwargs["action_type"] == NotificationActionType.CHAT
        assert call_kwargs["action_id"] == sender_id  # deep link abre o chat com o remetente

    @pytest.mark.asyncio
    async def test_does_not_raise_when_notify_fails(self):
        """Deve retornar o resultado mesmo quando notify() lança exceção."""
        sender_id = uuid4()
        receiver_id = uuid4()
        result = make_message_response(sender_id=sender_id, receiver_id=receiver_id)

        wrapped = MagicMock()
        wrapped.execute = AsyncMock(return_value=result)
        sender_user = MagicMock()
        sender_user.full_name = "Carlos"
        wrapped.user_repository = AsyncMock()
        wrapped.user_repository.get_by_id = AsyncMock(return_value=sender_user)

        notification_svc = AsyncMock()
        notification_svc.notify.side_effect = ConnectionError("WebSocket offline")

        dto = SendMessageDTO(receiver_id=receiver_id, content="Teste")
        decorator = NotifyOnSendMessage(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        # Não deve lançar exceção
        returned = await decorator.execute(sender_id, dto)
        assert returned == result
