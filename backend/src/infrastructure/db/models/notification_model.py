"""
Notification SQLAlchemy Model

Modelo de banco de dados para notificações dos usuários.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.notification import (
    Notification,
    NotificationActionType,
    NotificationType,
)
from src.infrastructure.db.database import Base


class NotificationModel(Base):
    """
    Modelo SQLAlchemy para tabela de notificações.

    Mapeado para a entidade de domínio Notification.
    """

    __tablename__ = "notifications"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Relacionamento com usuário
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e conteúdo
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Deep link
    action_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    action_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Estado
    is_read: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relacionamento com usuário
    user = relationship(
        "UserModel",
        back_populates="notifications",
        passive_deletes=True,
    )

    # Índices compostos para queries por usuário
    # Nota: o índice parcial WHERE is_read = FALSE é criado via op.execute() na migration
    __table_args__ = (
        Index("ix_notifications_user_created", "user_id", "created_at"),
    )

    def to_entity(self) -> Notification:
        """Converte o modelo para entidade de domínio."""
        return Notification(
            id=self.id,
            user_id=self.user_id,
            type=NotificationType(self.type),
            title=self.title,
            body=self.body,
            action_type=NotificationActionType(self.action_type) if self.action_type else None,
            action_id=self.action_id,
            is_read=self.is_read,
            created_at=self.created_at,
            read_at=self.read_at,
        )

    @classmethod
    def from_entity(cls, notification: Notification) -> "NotificationModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type.value,
            title=notification.title,
            body=notification.body,
            action_type=notification.action_type.value if notification.action_type else None,
            action_id=notification.action_id,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )

    def __repr__(self) -> str:
        return f"<NotificationModel(id={self.id}, user_id={self.user_id}, type={self.type})>"
