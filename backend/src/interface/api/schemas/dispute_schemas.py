"""
Dispute Schemas

Schemas Pydantic para validação de requests e responses do sistema de disputas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Request Schemas
# =============================================================================


class OpenDisputeRequest(BaseModel):
    """Schema para abertura de disputa pelo aluno."""

    reason: str = Field(
        ...,
        pattern=r"^(no_show|vehicle_problem|other)$",
        description="Motivo da disputa: no_show, vehicle_problem, other",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Descrição detalhada do problema ocorrido",
    )
    contact_phone: str = Field(
        ...,
        min_length=8,
        max_length=20,
        description="Telefone de contato do aluno",
    )
    contact_email: str = Field(
        ...,
        max_length=255,
        description="E-mail de contato do aluno",
    )


class ResolveDisputeRequest(BaseModel):
    """Schema para resolução de disputa pelo administrador."""

    resolution: str = Field(
        ...,
        pattern=r"^(favor_instructor|favor_student|rescheduled)$",
        description="Tipo de resolução: favor_instructor, favor_student, rescheduled",
    )
    resolution_notes: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Notas do administrador sobre a resolução",
    )
    refund_type: str | None = Field(
        None,
        pattern=r"^(full|partial)$",
        description="Tipo de reembolso (obrigatório se favor_student): full ou partial",
    )
    new_datetime: datetime | None = Field(
        None,
        description="Nova data/hora para reagendamento (obrigatório se rescheduled)",
    )


class UpdateDisputeStatusRequest(BaseModel):
    """Schema para atualização de status da disputa (OPEN → UNDER_REVIEW)."""

    new_status: str = Field(
        ...,
        pattern=r"^(under_review)$",
        description="Novo status: under_review",
    )


# =============================================================================
# Response Schemas
# =============================================================================


class DisputeResponse(BaseModel):
    """Schema de resposta para uma disputa."""

    id: UUID
    scheduling_id: UUID
    opened_by: UUID
    reason: str
    description: str
    contact_phone: str
    contact_email: str
    status: str
    resolution: str | None = None
    resolution_notes: str | None = None
    refund_type: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Dados enriquecidos (opcionais)
    student_name: str | None = None
    instructor_name: str | None = None
    scheduled_datetime: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DisputeListResponse(BaseModel):
    """Schema de resposta para lista paginada de disputas."""

    disputes: list[DisputeResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool
