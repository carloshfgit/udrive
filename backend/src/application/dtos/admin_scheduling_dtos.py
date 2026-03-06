"""
Admin Scheduling DTOs

Data Transfer Objects para operações administrativas de agendamentos.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.entities.scheduling_status import SchedulingStatus


# === Input DTOs ===


@dataclass(frozen=True)
class ListAllSchedulingsDTO:
    """DTO para listagem de agendamentos com filtros."""

    status: SchedulingStatus | None = None
    student_id: UUID | None = None
    instructor_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class AdminCancelSchedulingDTO:
    """DTO para cancelamento de agendamento pelo administrador."""

    scheduling_id: UUID = None  # type: ignore
    admin_id: UUID = None  # type: ignore
    reason: str = ""


# === Output DTOs ===


@dataclass
class SchedulingAdminResponseDTO:
    """DTO de resposta para um agendamento (visão admin)."""

    id: UUID
    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    status: str
    price: float
    student_name: str | None = None
    instructor_name: str | None = None
    payment_status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class SchedulingListResponseDTO:
    """DTO de resposta para lista paginada de agendamentos."""

    schedulings: list[SchedulingAdminResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool
