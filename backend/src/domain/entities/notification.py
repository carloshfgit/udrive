"""
Notification Entity

Entidade de domínio representando uma notificação do sistema.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class NotificationType(str, Enum):
    """Tipos de notificação suportados pelo sistema."""

    NEW_SCHEDULING = "NEW_SCHEDULING"
    RESCHEDULE_REQUESTED = "RESCHEDULE_REQUESTED"
    RESCHEDULE_RESPONDED = "RESCHEDULE_RESPONDED"
    NEW_CHAT_MESSAGE = "NEW_CHAT_MESSAGE"
    LESSON_REMINDER = "LESSON_REMINDER"
    PAYMENT_STATUS_CHANGED = "PAYMENT_STATUS_CHANGED"
    SCHEDULING_STATUS_CHANGED = "SCHEDULING_STATUS_CHANGED"
    REVIEW_REQUEST = "REVIEW_REQUEST"
    DISPUTE_OPENED = "DISPUTE_OPENED"
    DISPUTE_RESOLVED = "DISPUTE_RESOLVED"


class NotificationActionType(str, Enum):
    """Tipo de destino do deep link ao clicar na notificação."""

    SCHEDULING = "SCHEDULING"
    CHAT = "CHAT"
    REVIEW = "REVIEW"
    PAYMENT = "PAYMENT"


@dataclass
class Notification:
    """
    Entidade de notificação do sistema GoDrive.

    Representa uma notificação enviada a um usuário (aluno ou instrutor),
    com suporte a histórico persistido e deep link para navegação.
    """

    user_id: UUID
    type: NotificationType
    title: str
    body: str
    action_type: NotificationActionType | None = None
    action_id: UUID | None = None
    is_read: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: datetime | None = None

    def mark_as_read(self) -> None:
        """Marca a notificação como lida."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
