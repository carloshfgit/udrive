"""
Student Lessons Router

Endpoints para gerenciamento de agendamentos do aluno.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.scheduling_dtos import CancelSchedulingDTO, CreateSchedulingDTO
from src.application.use_cases.scheduling import CancelSchedulingUseCase, CreateSchedulingUseCase
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import AvailabilityRepo, CurrentStudent, SchedulingRepo
from src.interface.api.schemas.scheduling_schemas import (
    CancellationResultResponse,
    CancelSchedulingRequest,
    CreateSchedulingRequest,
    SchedulingListResponse,
    SchedulingResponse,
)

router = APIRouter(prefix="/lessons", tags=["Student - Lessons"])


@router.post(
    "",
    response_model=SchedulingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar agendamento",
    description="Solicita um novo agendamento de aula.",
)
async def create_scheduling(
    request: CreateSchedulingRequest,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    availability_repo: AvailabilityRepo,
) -> SchedulingResponse:
    """Solicita um novo agendamento de aula."""
    use_case = CreateSchedulingUseCase(scheduling_repo, availability_repo)

    dto = CreateSchedulingDTO(
        student_id=current_user.id,
        instructor_id=request.instructor_id,
        scheduled_datetime=request.scheduled_datetime,
        duration_minutes=request.duration_minutes,
    )

    result = await use_case.execute(dto)
    return SchedulingResponse.model_validate(result)


@router.get(
    "",
    response_model=SchedulingListResponse,
    summary="Listar agendamentos",
    description="Lista agendamentos do aluno atual.",
)
async def list_student_schedulings(
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    status_filter: SchedulingStatus | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
) -> SchedulingListResponse:
    """Lista agendamentos do aluno."""
    offset = (page - 1) * limit
    schedulings = await scheduling_repo.list_by_student(
        student_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    total = await scheduling_repo.count_by_student(
        student_id=current_user.id,
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
    description="Obtém detalhes de um agendamento específico.",
)
async def get_scheduling(
    scheduling_id: UUID,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse:
    """Obtém detalhes de um agendamento específico."""
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este agendamento",
        )

    return SchedulingResponse.model_validate(scheduling)


@router.post(
    "/{scheduling_id}/cancel",
    response_model=CancellationResultResponse,
    summary="Cancelar agendamento",
    description="Cancela um agendamento.",
)
async def cancel_scheduling(
    scheduling_id: UUID,
    request: CancelSchedulingRequest,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
) -> CancellationResultResponse:
    """Cancela um agendamento."""
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado a este agendamento",
        )

    use_case = CancelSchedulingUseCase(scheduling_repo)
    dto = CancelSchedulingDTO(
        scheduling_id=scheduling_id,
        cancelled_by=current_user.id,
        reason=request.reason,
    )

    result = await use_case.execute(dto)
    return CancellationResultResponse(
        scheduling_id=result.scheduling_id,
        status=result.status.value if hasattr(result.status, 'value') else str(result.status),
        refund_percentage=int(result.refund_percentage * 100) if hasattr(result, 'refund_percentage') else 0,
        refund_amount=result.refund_amount if hasattr(result, 'refund_amount') else 0,
        message=f"Agendamento cancelado com sucesso.",
    )
