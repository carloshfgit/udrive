"""
Instructor Schedule Router

Endpoints para gerenciamento de agenda do instrutor.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.application.use_cases.scheduling import CompleteSchedulingUseCase, ConfirmSchedulingUseCase
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import CurrentInstructor, SchedulingRepo
from src.interface.api.schemas.scheduling_schemas import SchedulingListResponse, SchedulingResponse

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

    use_case = ConfirmSchedulingUseCase(scheduling_repo)
    from src.application.dtos.scheduling_dtos import ConfirmSchedulingDTO
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

    use_case = CompleteSchedulingUseCase(scheduling_repo)
    result = await use_case.execute(scheduling_id)
    return SchedulingResponse.model_validate(result)
