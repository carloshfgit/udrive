"""
RefreshToken SQLAlchemy Model

Modelo de banco de dados para refresh tokens.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.refresh_token import RefreshToken
from src.infrastructure.db.database import Base


class RefreshTokenModel(Base):
    """
    Modelo SQLAlchemy para tabela de refresh tokens.

    Mapeado para a entidade de domínio RefreshToken.
    """

    __tablename__ = "refresh_tokens"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Token hash (não armazenamos o token em texto plano)
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Relacionamento com usuário
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Expiração e status
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relacionamentos
    user = relationship("UserModel", back_populates="refresh_tokens")

    # Índices
    __table_args__ = (
        Index("ix_refresh_tokens_user_id_is_revoked", "user_id", "is_revoked"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )

    def to_entity(self) -> RefreshToken:
        """Converte o modelo para entidade de domínio."""
        return RefreshToken(
            id=self.id,
            token_hash=self.token_hash,
            user_id=self.user_id,
            expires_at=self.expires_at,
            is_revoked=self.is_revoked,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, token: RefreshToken) -> "RefreshTokenModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=token.id,
            token_hash=token.token_hash,
            user_id=token.user_id,
            expires_at=token.expires_at,
            is_revoked=token.is_revoked,
            created_at=token.created_at,
        )

    def __repr__(self) -> str:
        return f"<RefreshTokenModel(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
