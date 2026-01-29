"""
User SQLAlchemy Model

Modelo de banco de dados para usuários.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.user import User
from src.domain.entities.user_type import UserType
from src.infrastructure.db.database import Base


class UserModel(Base):
    """
    Modelo SQLAlchemy para tabela de usuários.

    Mapeado para a entidade de domínio User.
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Campos de identificação
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Tipo e status
    user_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
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
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relacionamentos
    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    instructor_profile = relationship(
        "InstructorProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_profile = relationship(
        "StudentProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_payments = relationship(
        "PaymentModel",
        foreign_keys="PaymentModel.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    instructor_payments = relationship(
        "PaymentModel",
        foreign_keys="PaymentModel.instructor_id",
        back_populates="instructor",
        cascade="all, delete-orphan",
    )
    transactions = relationship(
        "TransactionModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Índices compostos
    __table_args__ = (
        Index("ix_users_email_is_active", "email", "is_active"),
        Index("ix_users_user_type_is_active", "user_type", "is_active"),
    )

    def to_entity(self) -> User:
        """Converte o modelo para entidade de domínio."""
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            user_type=UserType(self.user_type),
            is_active=self.is_active,
            is_verified=self.is_verified,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, user: User) -> "UserModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            user_type=user.user_type.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, type={self.user_type})>"
