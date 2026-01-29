"""
Availability SQLAlchemy Model

Modelo de banco de dados para disponibilidade de instrutores.
"""

import uuid
from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.availability import Availability
from src.infrastructure.db.database import Base


class AvailabilityModel(Base):
    """
    Modelo SQLAlchemy para slots de disponibilidade.
    """

    __tablename__ = "instructor_availability"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Key
    instructor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Horários
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )  # 0=Monday, 6=Sunday
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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
    instructor = relationship(
        "UserModel",
        foreign_keys=[instructor_id],
        backref="availabilities",
    )

    # Constraints e Índices
    __table_args__ = (
        # Garante que um instrutor não tenha slots duplicados para o mesmo dia e hora de inicio
        UniqueConstraint(
            "instructor_id",
            "day_of_week",
            "start_time",
            name="uq_instructor_availability_slot",
        ),
        Index("ix_availability_instructor", "instructor_id"),
        Index("ix_availability_day_time", "day_of_week", "start_time"),
    )

    def to_entity(self) -> Availability:
        """Converte o modelo para entidade de domínio."""
        return Availability(
            id=self.id,
            instructor_id=self.instructor_id,
            day_of_week=self.day_of_week,
            start_time=self.start_time,
            end_time=self.end_time,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, availability: Availability) -> "AvailabilityModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
            id=availability.id,
            instructor_id=availability.instructor_id,
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_active=availability.is_active,
            created_at=availability.created_at,
            updated_at=availability.updated_at,
        )
