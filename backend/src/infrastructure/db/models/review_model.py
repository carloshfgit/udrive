"""
Review SQLAlchemy Model

Modelo de banco de dados para avaliações de aulas.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.review import Review
from src.infrastructure.db.database import Base


class ReviewModel(Base):
    """
    Modelo SQLAlchemy para tabela de avaliações.
    """

    __tablename__ = "reviews"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Keys
    scheduling_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedulings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    instructor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Detalhes da avaliação
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relacionamentos
    scheduling = relationship("SchedulingModel", backref="review")
    student = relationship("UserModel", foreign_keys=[student_id])
    instructor = relationship("UserModel", foreign_keys=[instructor_id])

    def to_entity(self) -> Review:
        """Converte o modelo para entidade de domínio."""
        student_name = None
        # Tenta pegar o nome do estudante se o relacionamento estiver carregado
        # Evita trigger de lazy load que causa MissingGreenlet em sessão async
        if "student" in self.__dict__ and self.student:
            student_name = self.student.full_name

        return Review(
            id=self.id,
            scheduling_id=self.scheduling_id,
            student_id=self.student_id,
            instructor_id=self.instructor_id,
            rating=self.rating,
            comment=self.comment,
            student_name=student_name,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, review: Review) -> "ReviewModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=review.id,
            scheduling_id=review.scheduling_id,
            student_id=review.student_id,
            instructor_id=review.instructor_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )
