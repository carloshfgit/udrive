"""
Message SQLAlchemy Model

Modelo de banco de dados para mensagens de chat.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.message import Message
from src.infrastructure.db.database import Base


class MessageModel(Base):
    """
    Modelo SQLAlchemy para tabela de mensagens.
    """

    __tablename__ = "messages"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Keys
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conteúdo e Status
    content: Mapped[str] = mapped_column(
        String, # Usando String sem limite para conteúdo de mensagem (Text no PG)
        nullable=False,
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relacionamentos
    sender = relationship(
        "UserModel",
        foreign_keys=[sender_id],
        back_populates="sent_messages",
    )
    receiver = relationship(
        "UserModel",
        foreign_keys=[receiver_id],
        back_populates="received_messages",
    )

    def to_entity(self) -> Message:
        """Converte o modelo para entidade de domínio."""
        return Message(
            id=self.id,
            sender_id=self.sender_id,
            receiver_id=self.receiver_id,
            content=self.content,
            timestamp=self.timestamp,
            is_read=self.is_read,
        )

    @classmethod
    def from_entity(cls, message: Message) -> "MessageModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            timestamp=message.timestamp,
            is_read=message.is_read,
        )

    def __repr__(self) -> str:
        return f"<MessageModel(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id})>"
