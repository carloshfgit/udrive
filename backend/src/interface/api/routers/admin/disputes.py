"""
Admin Disputes Router

Endpoints para gerenciamento de disputas pelo administrador.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.dispute_dtos import (
    ListDisputesDTO,
    ResolveDisputeDTO,
    UpdateDisputeStatusDTO,
)
from src.application.use_cases.scheduling.list_disputes import ListDisputesUseCase
from src.application.use_cases.scheduling.resolve_dispute import (
    DisputeNotFoundException,
    ResolveDisputeUseCase,
)
from src.domain.entities.dispute_enums import DisputeStatus
from src.interface.api.dependencies import (
    CurrentAdmin,
    DisputeRepo,
    SchedulingRepo,
)
from src.interface.api.schemas.dispute_schemas import (
    DisputeListResponse,
    DisputeResponse,
    ResolveDisputeRequest,
    UpdateDisputeStatusRequest,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/disputes", tags=["Admin - Disputes"])


@router.get(
    "",
    response_model=DisputeListResponse,
    summary="Listar disputas",
    description="Lista disputas com filtro por status e paginação.",
)
async def list_disputes(
    current_user: CurrentAdmin,
    dispute_repo: DisputeRepo,
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filtro por status: open, under_review, resolved",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> DisputeListResponse:
    """Lista disputas para o painel administrativo."""
    use_case = ListDisputesUseCase(dispute_repository=dispute_repo)

    offset = (page - 1) * limit
    dto = ListDisputesDTO(
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    result = await use_case.execute(dto)

    return DisputeListResponse(
        disputes=[DisputeResponse.model_validate(d.__dict__) for d in result.disputes],
        total_count=result.total_count,
        limit=result.limit,
        offset=result.offset,
        has_more=result.has_more,
    )


@router.get(
    "/{dispute_id}",
    response_model=DisputeResponse,
    summary="Detalhes da disputa",
    description="Obtém detalhes completos de uma disputa específica.",
)
async def get_dispute(
    dispute_id: UUID,
    current_user: CurrentAdmin,
    dispute_repo: DisputeRepo,
) -> DisputeResponse:
    """Obtém detalhes de uma disputa específica."""
    dispute = await dispute_repo.get_by_id(dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada",
        )

    return DisputeResponse(
        id=dispute.id,
        scheduling_id=dispute.scheduling_id,
        opened_by=dispute.opened_by,
        reason=dispute.reason.value,
        description=dispute.description,
        contact_phone=dispute.contact_phone,
        contact_email=dispute.contact_email,
        status=dispute.status.value,
        resolution=dispute.resolution.value if dispute.resolution else None,
        resolution_notes=dispute.resolution_notes,
        refund_type=dispute.refund_type,
        resolved_by=dispute.resolved_by,
        resolved_at=dispute.resolved_at,
        created_at=dispute.created_at,
        updated_at=dispute.updated_at,
    )


@router.post(
    "/{dispute_id}/resolve",
    response_model=DisputeResponse,
    summary="Resolver disputa",
    description="Resolve uma disputa com decisão do administrador.",
)
async def resolve_dispute(
    dispute_id: UUID,
    request: ResolveDisputeRequest,
    current_user: CurrentAdmin,
    dispute_repo: DisputeRepo,
    scheduling_repo: SchedulingRepo,
) -> DisputeResponse:
    """Resolve uma disputa."""
    use_case = ResolveDisputeUseCase(
        dispute_repository=dispute_repo,
        scheduling_repository=scheduling_repo,
    )

    dto = ResolveDisputeDTO(
        dispute_id=dispute_id,
        admin_id=current_user.id,
        resolution=request.resolution,
        resolution_notes=request.resolution_notes,
        refund_type=request.refund_type,
        new_datetime=request.new_datetime,
    )

    try:
        result = await use_case.execute(dto)
        return DisputeResponse.model_validate(result.__dict__)
    except DisputeNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{dispute_id}/status",
    response_model=DisputeResponse,
    summary="Alterar status da disputa",
    description="Altera o status de uma disputa (ex: OPEN → UNDER_REVIEW).",
)
async def update_dispute_status(
    dispute_id: UUID,
    request: UpdateDisputeStatusRequest,
    current_user: CurrentAdmin,
    dispute_repo: DisputeRepo,
) -> DisputeResponse:
    """Altera o status de uma disputa."""
    dispute = await dispute_repo.get_by_id(dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada",
        )

    # Validar transição de status
    try:
        new_status = DisputeStatus(request.new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido: {request.new_status}",
        )

    if dispute.status == DisputeStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar o status de uma disputa já resolvida.",
        )

    dispute.status = new_status
    updated = await dispute_repo.update(dispute)

    return DisputeResponse(
        id=updated.id,
        scheduling_id=updated.scheduling_id,
        opened_by=updated.opened_by,
        reason=updated.reason.value,
        description=updated.description,
        contact_phone=updated.contact_phone,
        contact_email=updated.contact_email,
        status=updated.status.value,
        resolution=updated.resolution.value if updated.resolution else None,
        resolution_notes=updated.resolution_notes,
        refund_type=updated.refund_type,
        resolved_by=updated.resolved_by,
        resolved_at=updated.resolved_at,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )
