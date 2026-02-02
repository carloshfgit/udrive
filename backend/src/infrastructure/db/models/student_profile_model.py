"""
StudentProfile SQLAlchemy Model

Modelo de banco de dados para perfis de alunos.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.student_profile import LearningStage, StudentProfile
from src.infrastructure.db.database import Base


class StudentProfileModel(Base):
    """
    Modelo SQLAlchemy para tabela de perfis de alunos.
    """

    __tablename__ = "student_profiles"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Key para User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Informações do perfil
    preferred_schedule: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=False,
    )
    license_category_goal: Mapped[str] = mapped_column(
        String(10),
        default="B",
        nullable=False,
    )
    learning_stage: Mapped[str] = mapped_column(
        String(50),
        default=LearningStage.BEGINNER,
        nullable=False,
        index=True,
    )
    notes: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    # Dados pessoais movidos para UserModel

    # Estatísticas
    total_lessons: Mapped[int] = mapped_column(
        default=0,
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
    user = relationship("UserModel", back_populates="student_profile")

    def to_entity(self) -> StudentProfile:
        """Converte o modelo para entidade de domínio."""
        return StudentProfile(
            id=self.id,
            user_id=self.user_id,
            preferred_schedule=self.preferred_schedule,
            license_category_goal=self.license_category_goal,
            learning_stage=self.learning_stage,
            notes=self.notes,
            total_lessons=self.total_lessons,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, profile: StudentProfile) -> "StudentProfileModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            preferred_schedule=profile.preferred_schedule,
            license_category_goal=profile.license_category_goal,
            learning_stage=profile.learning_stage,
            notes=profile.notes,
            total_lessons=profile.total_lessons,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    def __repr__(self) -> str:
        return f"<StudentProfileModel(id={self.id}, user_id={self.user_id}, stage={self.learning_stage})>"
