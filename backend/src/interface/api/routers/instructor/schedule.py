"""
Instructor Schedule Router

Endpoints para gerenciamento de agenda do instrutor.
"""

from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.scheduling_dtos import (
    CancelSchedulingDTO,
    CompleteSchedulingDTO,
    ConfirmSchedulingDTO,
)
from src.application.use_cases.scheduling import (
    CancelSchedulingUseCase,
    CompleteSchedulingUseCase,
    ConfirmSchedulingUseCase,
)
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import CurrentInstructor, SchedulingRepo, UserRepo
from src.interface.api.schemas.scheduling_schemas import (
    CancellationResultResponse,
    SchedulingListResponse,
    SchedulingResponse,
)

router = APIRouter(prefix="/schedule", tags=["Instructor - Schedule"])


@router.get(
    "",
    response_model=SchedulingListResponse,
    summary="Listar agenda",
    description="Lista agendamentos do instrutor.",
)
async def list_instructor_schedule(
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    status_filter: SchedulingStatus | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
) -> SchedulingListResponse:
    """Lista agendamentos do instrutor."""
    offset = (page - 1) * limit
    schedulings = await scheduling_repo.list_by_instructor(
        instructor_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    total = await scheduling_repo.count_by_instructor(
        instructor_id=current_user.id,
        status=status_filter,
    )

    return SchedulingListResponse(
        schedulings=[SchedulingResponse.model_validate(s) for s in schedulings],
        total_count=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total,
    )


@router.get(
    "/by-date",
    response_model=SchedulingListResponse,
    summary="Listar agenda por data",
    description="Lista agendamentos do instrutor para uma data específica.",
)
async def list_schedule_by_date(
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    target_date: date = Query(..., alias="date", description="Data no formato YYYY-MM-DD"),
) -> SchedulingListResponse:
    """Lista agendamentos para uma data específica."""
    schedulings = await scheduling_repo.list_by_instructor_and_date(
        instructor_id=current_user.id,
        target_date=target_date,
    )
    return SchedulingListResponse(
        schedulings=[SchedulingResponse.model_validate(s) for s in schedulings],
        total_count=len(schedulings),
        limit=len(schedulings),
        offset=0,
        has_more=False,
    )

@router.get(
    "/dates-with-schedulings",
    summary="Listar datas com aulas",
    description="Retorna lista de datas que possuem agendamentos no mês.",
)
async def get_scheduling_dates(
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    year: int = Query(..., ge=2020, le=2050, description="Ano"),
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
) -> dict:
    """Lista datas com agendamentos no mês."""
    dates = await scheduling_repo.get_scheduling_dates_for_month(
        instructor_id=current_user.id,
        year=year,
        month=month,
    )
    return {
        "dates": [d.isoformat() for d in dates],
        "year": year,
        "month": month,
    }


@router.get(
    "/{scheduling_id}",
    response_model=SchedulingResponse,
    summary="Obter agendamento",
    description="Obtém detalhes de um agendamento.",
)
async def get_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse:
    """Obtém detalhes de um agendamento."""
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este agendamento",
        )

    return SchedulingResponse.model_validate(scheduling)


@router.post(
    "/{scheduling_id}/confirm",
    response_model=SchedulingResponse,
    summary="Confirmar agendamento",
    description="Confirma um agendamento pendente.",
)
async def confirm_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Confirma um agendamento pendente."""
    # Verificar permissão
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o instrutor pode confirmar",
        )

    use_case = ConfirmSchedulingUseCase(scheduling_repo, user_repo)
    dto = ConfirmSchedulingDTO(
        scheduling_id=scheduling_id,
        instructor_id=current_user.id,
    )
    result = await use_case.execute(dto)
    return SchedulingResponse.model_validate(result)


@router.post(
    "/{scheduling_id}/complete",
    response_model=SchedulingResponse,
    summary="Concluir agendamento",
    description="Marca um agendamento como concluído.",
)
async def complete_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Marca um agendamento como concluído."""
    # Verificar permissão
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o instrutor pode concluir",
        )

    use_case = CompleteSchedulingUseCase(scheduling_repo, user_repo)
    dto = CompleteSchedulingDTO(
        scheduling_id=scheduling_id,
        instructor_id=current_user.id,
    )
    result = await use_case.execute(dto)
    return SchedulingResponse.model_validate(result)


@router.post(
    "/{scheduling_id}/cancel",
    response_model=CancellationResultResponse,
    summary="Cancelar agendamento",
    description="Cancela um agendamento pendente ou confirmado.",
)
async def cancel_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
    reason: str | None = Query(None, description="Motivo do cancelamento"),
) -> CancellationResultResponse:
    """Cancela um agendamento."""
    # Verificar permissão
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este agendamento",
        )

    try:
        use_case = CancelSchedulingUseCase(scheduling_repo, user_repo)
        dto = CancelSchedulingDTO(
            scheduling_id=scheduling_id,
            cancelled_by=current_user.id,
            reason=reason,
        )
        result = await use_case.execute(dto)
        return CancellationResultResponse(
            scheduling_id=result.scheduling_id,
            status=result.status,
            refund_percentage=result.refund_percentage,
            refund_amount=result.refund_amount,
            cancelled_at=result.cancelled_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )