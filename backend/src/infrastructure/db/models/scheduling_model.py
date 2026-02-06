"""
Scheduling SQLAlchemy Model

Modelo de banco de dados para agendamentos.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.infrastructure.db.database import Base


class SchedulingModel(Base):
    """
    Modelo SQLAlchemy para tabela de agendamentos.
    """

    __tablename__ = "schedulings"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Keys
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

    # Detalhes do agendamento
    scheduled_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    duration_minutes: Mapped[int] = mapped_column(
        default=50,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Status e Cancelamento
    status: Mapped[SchedulingStatus] = mapped_column(
        Enum(
            SchedulingStatus,
            name="scheduling_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=SchedulingStatus.PENDING,
        nullable=False,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    cancelled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relacionamentos
    student = relationship(
        "UserModel",
        foreign_keys=[student_id],
        backref="student_schedulings",
    )
    instructor = relationship(
        "UserModel",
        foreign_keys=[instructor_id],
        backref="instructor_schedulings",
    )
    canceller = relationship(
        "UserModel",
        foreign_keys=[cancelled_by],
    )
    payment = relationship(
        "PaymentModel",
        back_populates="scheduling",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Índices
    __table_args__ = (
        Index("ix_schedulings_student_date", "student_id", "scheduled_datetime"),
        Index("ix_schedulings_instructor_date", "instructor_id", "scheduled_datetime"),
        Index("ix_schedulings_status", "status"),
    )

    def to_entity(self) -> Scheduling:
        """Converte o modelo para entidade de domínio."""
        return Scheduling(
            id=self.id,
            student_id=self.student_id,
            instructor_id=self.instructor_id,
            scheduled_datetime=self.scheduled_datetime,
            duration_minutes=self.duration_minutes,
            price=self.price,
            status=self.status,
            cancellation_reason=self.cancellation_reason,
            cancelled_by=self.cancelled_by,
            cancelled_at=self.cancelled_at,
            completed_at=self.completed_at,
            started_at=self.started_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
            student_name=self.student.full_name if self.student else None,
            instructor_name=self.instructor.full_name if self.instructor else None,
            has_review=True if hasattr(self, "review") and self.review else False,
        )

    @classmethod
    def from_entity(cls, scheduling: Scheduling) -> "SchedulingModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=scheduling.id,
            student_id=scheduling.student_id,
            instructor_id=scheduling.instructor_id,
            scheduled_datetime=scheduling.scheduled_datetime,
            duration_minutes=scheduling.duration_minutes,
            price=scheduling.price,
            status=scheduling.status,
            cancellation_reason=scheduling.cancellation_reason,
            cancelled_by=scheduling.cancelled_by,
            cancelled_at=scheduling.cancelled_at,
            completed_at=scheduling.completed_at,
            started_at=scheduling.started_at,
            created_at=scheduling.created_at,
            updated_at=scheduling.updated_at,
        )
