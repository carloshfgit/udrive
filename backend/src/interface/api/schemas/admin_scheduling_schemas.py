"""
Admin Scheduling Schemas

Schemas Pydantic para validação de requests e responses dos endpoints admin de agendamentos.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Request Schemas
# =============================================================================


class AdminCancelRequest(BaseModel):
    """Schema para cancelamento administrativo de agendamento."""

    reason: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Motivo do cancelamento pelo administrador",
    )


# =============================================================================
# Response Schemas
# =============================================================================


class SchedulingAdminResponse(BaseModel):
    """Schema de resposta para um agendamento (visão admin)."""

    id: UUID
    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    status: str
    price: float
    student_name: str | None = None
    instructor_name: str | None = None
    payment_status: str | None = None
    lesson_category: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SchedulingListResponse(BaseModel):
    """Schema de resposta para lista paginada de agendamentos."""

    schedulings: list[SchedulingAdminResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool
