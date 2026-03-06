"""
Dispute DTOs

Data Transfer Objects para operações de disputa.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


# === Input DTOs ===


@dataclass(frozen=True)
class OpenDisputeDTO:
    """DTO para abertura de disputa pelo aluno."""

    scheduling_id: UUID
    student_id: UUID
    reason: str
    description: str
    contact_phone: str
    contact_email: str


@dataclass(frozen=True)
class ResolveDisputeDTO:
    """DTO para resolução de disputa pelo administrador."""

    dispute_id: UUID
    admin_id: UUID
    resolution: str  # "favor_instructor", "favor_student", "rescheduled"
    resolution_notes: str
    refund_type: str | None = None  # "full" ou "partial"
    new_datetime: datetime | None = None  # obrigatório se resolution == "rescheduled"


@dataclass(frozen=True)
class UpdateDisputeStatusDTO:
    """DTO para atualizar status da disputa (ex: OPEN -> UNDER_REVIEW)."""

    dispute_id: UUID
    admin_id: UUID
    new_status: str  # "under_review"


@dataclass(frozen=True)
class ListDisputesDTO:
    """DTO para listagem de disputas com filtros."""

    status: str | None = None
    limit: int = 50
    offset: int = 0


# === Output DTOs ===


@dataclass
class DisputeResponseDTO:
    """DTO de resposta para uma disputa."""

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
    price: float | None = None


@dataclass
class DisputeListResponseDTO:
    """DTO de resposta para lista paginada de disputas."""

    disputes: list[DisputeResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool
