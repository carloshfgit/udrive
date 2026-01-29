"""
Scheduling Schemas

Schemas Pydantic para validação de requests e responses de agendamento e disponibilidade.
"""

from datetime import datetime, time
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.scheduling_status import SchedulingStatus


# =============================================================================
# Availability Schemas
# =============================================================================

class CreateAvailabilityRequest(BaseModel):
    """Schema para criação de slot de disponibilidade."""

    day_of_week: int = Field(..., ge=0, le=6, description="Dia da semana (0=Segunda, 6=Domingo)")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora de início (HH:MM)")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Hora de término (HH:MM)")

    # Validators podem ser adicionados para converter str -> time se necessário,
    # mas o use case espera objetos time. Faremos a conversão no router ou aqui.
    # Vamos receber como string para validação regex e converter no router/usecase.


class UpdateAvailabilityRequest(BaseModel):
    """Schema para atualização de slot."""

    start_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    end_time: str | None = Field(None, pattern=r"^\d{2}:\d{2}$")
    is_active: bool | None = None


class AvailabilityResponse(BaseModel):
    """Schema de resposta para disponibilidade."""

    id: UUID
    instructor_id: UUID
    day_of_week: int
    day_name: str
    start_time: str
    end_time: str
    is_active: bool
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class AvailabilityListResponse(BaseModel):
    """Schema de listagem de disponibilidades."""

    availabilities: list[AvailabilityResponse]
    instructor_id: UUID
    total_count: int


# =============================================================================
# Scheduling Schemas
# =============================================================================

class CreateSchedulingRequest(BaseModel):
    """Schema para criar agendamento."""

    instructor_id: UUID
    scheduled_datetime: datetime
    duration_minutes: int = Field(50, ge=30, le=120)


class CancelSchedulingRequest(BaseModel):
    """Schema para cancelar agendamento."""

    reason: str = Field(..., min_length=5, max_length=500)


class SchedulingResponse(BaseModel):
    """Schema de resposta para agendamento."""

    id: UUID
    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    duration_minutes: int
    price: Decimal
    status: SchedulingStatus
    cancellation_reason: str | None = None
    cancelled_by: UUID | None = None
    cancelled_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    
    # Campos enriquecidos (opcionais, preenchidos se disponíveis)
    student_name: str | None = None
    instructor_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SchedulingListResponse(BaseModel):
    """Schema de listagem de agendamentos."""

    schedulings: list[SchedulingResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool


class CancellationResultResponse(BaseModel):
    """Schema de resultado de cancelamento."""
    
    scheduling_id: UUID
    status: str
    refund_percentage: int
    refund_amount: Decimal
    message: str
