"""
Scheduling DTOs

Data Transfer Objects para operações de agendamento e disponibilidade.
"""

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from src.domain.entities.scheduling_status import SchedulingStatus


# === Input DTOs ===


@dataclass(frozen=True)
class CreateSchedulingDTO:
    """DTO para criação de agendamento."""

    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    duration_minutes: int = 50


@dataclass(frozen=True)
class CancelSchedulingDTO:
    """DTO para cancelamento de agendamento."""

    scheduling_id: UUID
    cancelled_by: UUID
    reason: str | None = None


@dataclass(frozen=True)
class ConfirmSchedulingDTO:
    """DTO para confirmação de agendamento pelo instrutor."""

    scheduling_id: UUID
    instructor_id: UUID


@dataclass(frozen=True)
class CompleteSchedulingDTO:
    """DTO para marcar agendamento como concluído."""

    scheduling_id: UUID
    instructor_id: UUID


@dataclass(frozen=True)
class ListSchedulingsDTO:
    """DTO para listagem de agendamentos com filtros."""

    user_id: UUID
    status: SchedulingStatus | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class CreateAvailabilityDTO:
    """DTO para criação de slot de disponibilidade."""

    instructor_id: UUID
    day_of_week: int
    start_time: time
    end_time: time


@dataclass(frozen=True)
class UpdateAvailabilityDTO:
    """DTO para atualização de slot de disponibilidade."""

    availability_id: UUID
    instructor_id: UUID
    start_time: time | None = None
    end_time: time | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class DeleteAvailabilityDTO:
    """DTO para remoção de slot de disponibilidade."""

    availability_id: UUID
    instructor_id: UUID


@dataclass(frozen=True)
class StartSchedulingDTO:
    """DTO para iniciar um agendamento."""

    scheduling_id: UUID
    user_id: UUID


# === Output DTOs ===


@dataclass
class SchedulingResponseDTO:
    """DTO de resposta para agendamento."""

    id: UUID
    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    duration_minutes: int
    price: Decimal
    status: str
    cancellation_reason: str | None = None
    cancelled_by: UUID | None = None
    cancelled_at: datetime | None = None
    completed_at: datetime | None = None
    started_at: datetime | None = None
    created_at: datetime | None = None

    # Dados opcionais enriquecidos
    student_name: str | None = None
    instructor_name: str | None = None


@dataclass
class CancellationResultDTO:
    """DTO de resultado de cancelamento com informações de reembolso."""

    scheduling_id: UUID
    status: str
    refund_percentage: int
    refund_amount: Decimal
    cancelled_at: datetime


@dataclass
class SchedulingListResponseDTO:
    """DTO de resposta para lista paginada de agendamentos."""

    schedulings: list[SchedulingResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool


@dataclass
class AvailabilityResponseDTO:
    """DTO de resposta para slot de disponibilidade."""

    id: UUID
    instructor_id: UUID
    day_of_week: int
    day_name: str
    start_time: str  # Formato HH:MM
    end_time: str  # Formato HH:MM
    is_active: bool
    duration_minutes: int


@dataclass
class AvailabilityListResponseDTO:
    """DTO de resposta para lista de disponibilidades."""

    availabilities: list[AvailabilityResponseDTO]
    instructor_id: UUID
    total_count: int
