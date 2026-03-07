"""
Admin Disputes Router

Endpoints para gerenciamento de disputas pelo administrador.
"""

from uuid import UUID

import structlog
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from src.application.use_cases.scheduling.scheduling_notification_decorators import (
    NotifyOnResolveDispute,
)
from src.domain.entities.dispute_enums import DisputeResolution, DisputeStatus
from src.interface.api.dependencies import (
    CurrentAdmin,
    DisputeRepo,
    NotificationServiceDep,
    PaymentRepo,
    SchedulingRepo,
    get_resolve_dispute_use_case,
)
from src.interface.api.schemas.dispute_schemas import (
    DisputeListResponse,
    DisputePaymentResponse,
    DisputePaymentsListResponse,
    DisputeResponse,
    ResolveDisputeRequest,
    UpdateDisputeStatusRequest,
)
from src.interface.websockets.event_dispatcher import get_event_dispatcher

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
    result = await dispute_repo.get_enriched_by_id(dispute_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada",
        )

    dispute, student_name, instructor_name, scheduled_datetime, price = result

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
        student_name=student_name,
        instructor_name=instructor_name,
        scheduled_datetime=scheduled_datetime,
        price=price,
    )


@router.get(
    "/{dispute_id}/payments",
    response_model=DisputePaymentsListResponse,
    summary="Listar pagamentos da disputa",
    description="Lista todos os pagamentos do checkout associado a uma disputa.",
)
async def get_dispute_payments(
    dispute_id: UUID,
    current_user: CurrentAdmin,
    dispute_repo: DisputeRepo,
    payment_repo: PaymentRepo,
    scheduling_repo: SchedulingRepo,
) -> DisputePaymentsListResponse:
    """Lista todos os pagamentos do grupo de checkout da disputa."""
    # 1. Buscar disputa
    dispute = await dispute_repo.get_by_id(dispute_id)
    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada",
        )

    # 2. Buscar pagamento do scheduling da disputa
    payment = await payment_repo.get_by_scheduling_id(dispute.scheduling_id)
    if payment is None:
        return DisputePaymentsListResponse(payments=[])

    # 3. Se tem preference_group_id, buscar todos do grupo; senão, retornar só este
    if payment.preference_group_id:
        payments = await payment_repo.get_by_preference_group_id(
            payment.preference_group_id
        )
    else:
        payments = [payment]

    # 4. Enriquecer com data do scheduling
    result = []
    for p in payments:
        scheduled_dt = None
        scheduling = await scheduling_repo.get_by_id(p.scheduling_id)
        if scheduling:
            scheduled_dt = scheduling.scheduled_datetime

        result.append(
            DisputePaymentResponse(
                id=p.id,
                scheduling_id=p.scheduling_id,
                amount=float(p.amount),
                status=p.status.value,
                mp_refund_id=p.mp_refund_id,
                refund_amount=float(p.refund_amount) if p.refund_amount else None,
                refunded_at=p.refunded_at,
                scheduled_datetime=scheduled_dt,
            )
        )

    return DisputePaymentsListResponse(payments=result)


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
    use_case: Annotated[NotifyOnResolveDispute, Depends(get_resolve_dispute_use_case)],
    scheduling_repo: SchedulingRepo,
) -> DisputeResponse:
    """Resolve uma disputa."""
    dto = ResolveDisputeDTO(
        dispute_id=dispute_id,
        admin_id=current_user.id,
        resolution=request.resolution,
        resolution_notes=request.resolution_notes,
        refund_type=request.refund_type,
        new_datetime=request.new_datetime,
        payment_ids_to_refund=request.payment_ids_to_refund,
    )

    try:
        result = await use_case.execute(dto)

        # Etapa 7 — WebSocket: emitir evento de disputa resolvida
        dispatcher = get_event_dispatcher()
        if dispatcher:
            try:
                scheduling = await scheduling_repo.get_by_id(result.scheduling_id)
                if scheduling:
                    from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
                    scheduling_dto = SchedulingResponseDTO(
                        id=scheduling.id,
                        student_id=scheduling.student_id,
                        instructor_id=scheduling.instructor_id,
                        scheduled_datetime=scheduling.scheduled_datetime,
                        duration_minutes=scheduling.duration_minutes,
                        price=scheduling.price,
                        status=scheduling.status.value if hasattr(scheduling.status, 'value') else str(scheduling.status),
                        student_name=scheduling.student_name,
                        instructor_name=scheduling.instructor_name,
                    )
                    await dispatcher.emit_dispute_resolved(
                        scheduling_dto, scheduling.student_id, scheduling.instructor_id
                    )
            except Exception as e:
                logger.error("event_dispatch_error", dispatch_event="dispute_resolved", error=str(e))

        return DisputeResponse.model_validate(result.__dict__)

        # Etapa 7 — WebSocket: emitir evento de disputa resolvida
        dispatcher = get_event_dispatcher()
        if dispatcher:
            try:
                scheduling = await scheduling_repo.get_by_id(result.scheduling_id)
                if scheduling:
                    from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
                    scheduling_dto = SchedulingResponseDTO(
                        id=scheduling.id,
                        student_id=scheduling.student_id,
                        instructor_id=scheduling.instructor_id,
                        scheduled_datetime=scheduling.scheduled_datetime,
                        duration_minutes=scheduling.duration_minutes,
                        price=scheduling.price,
                        status=scheduling.status.value if hasattr(scheduling.status, 'value') else str(scheduling.status),
                        student_name=scheduling.student_name,
                        instructor_name=scheduling.instructor_name,
                    )
                    await dispatcher.emit_dispute_resolved(
                        scheduling_dto, scheduling.student_id, scheduling.instructor_id
                    )
            except Exception as e:
                logger.error("event_dispatch_error", dispatch_event="dispute_resolved", error=str(e))

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
    await dispute_repo.update(dispute)

    # Buscar dados enriquecidos para retorno
    result = await dispute_repo.get_enriched_by_id(dispute_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disputa não encontrada após atualização",
        )

    updated, student_name, instructor_name, scheduled_datetime, price = result

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
        student_name=student_name,
        instructor_name=instructor_name,
        scheduled_datetime=scheduled_datetime,
        price=price,
    )
