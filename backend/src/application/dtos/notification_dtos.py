"""
Notification DTOs

Data Transfer Objects para operações de notificações.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


# === Input DTOs ===


@dataclass(frozen=True)
class CreateNotificationInput:
    """DTO de entrada para criação de uma notificação."""

    user_id: UUID
    type: str  # NotificationType.value
    title: str
    body: str
    action_type: str | None = None  # NotificationActionType.value
    action_id: UUID | None = None


@dataclass(frozen=True)
class MarkAsReadInput:
    """DTO de entrada para marcar notificação como lida."""

    notification_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class ListNotificationsInput:
    """DTO de entrada para listagem paginada de notificações."""

    user_id: UUID
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class RegisterPushTokenInput:
    """DTO de entrada para registrar push token de dispositivo."""

    user_id: UUID
    token: str
    device_id: str | None = None
    platform: str | None = None  # 'ios' | 'android'


# === Output DTOs ===


@dataclass
class NotificationResponseDTO:
    """DTO de resposta para uma notificação."""

    id: UUID
    type: str
    title: str
    body: str
    action_type: str | None
    action_id: UUID | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None


@dataclass
class NotificationListResponseDTO:
    """DTO de resposta para lista paginada de notificações."""

    notifications: list[NotificationResponseDTO]
    unread_count: int
    total: int
    limit: int
    offset: int
    has_more: bool


@dataclass
class UnreadCountDTO:
    """DTO de resposta para contagem de notificações não lidas."""

    count: int
