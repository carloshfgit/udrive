"""
PushToken SQLAlchemy Model

Modelo de banco de dados para tokens de push notification dos dispositivos.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.push_token import PushToken
from src.infrastructure.db.database import Base


class PushTokenModel(Base):
    """
    Modelo SQLAlchemy para tabela de push tokens.

    Armazena os Expo Push Tokens dos dispositivos dos usuários para
    envio de notificações push quando o app está em background.
    """

    __tablename__ = "push_tokens"

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

    # Token do dispositivo
    token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    device_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    platform: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    # Estado
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relacionamento com usuário
    user = relationship(
        "UserModel",
        back_populates="push_tokens",
        passive_deletes=True,
    )

    def to_entity(self) -> PushToken:
        """Converte o modelo para entidade de domínio."""
        return PushToken(
            id=self.id,
            user_id=self.user_id,
            token=self.token,
            device_id=self.device_id,
            platform=self.platform,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, push_token: PushToken) -> "PushTokenModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=push_token.id,
            user_id=push_token.user_id,
            token=push_token.token,
            device_id=push_token.device_id,
            platform=push_token.platform,
            is_active=push_token.is_active,
            created_at=push_token.created_at,
            updated_at=push_token.updated_at,
        )

    def __repr__(self) -> str:
        return f"<PushTokenModel(id={self.id}, user_id={self.user_id}, platform={self.platform})>"
