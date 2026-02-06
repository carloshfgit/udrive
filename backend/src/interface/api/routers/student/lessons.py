"""
Student Lessons Router

Endpoints para gerenciamento de agendamentos do aluno.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.scheduling_dtos import CancelSchedulingDTO, CreateSchedulingDTO
from src.application.use_cases.create_review_use_case import CreateReviewUseCase
from src.application.use_cases.scheduling import CancelSchedulingUseCase, CreateSchedulingUseCase
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import (
    AvailabilityRepo,
    CurrentStudent,
    InstructorRepo,
    ReviewRepo,
    SchedulingRepo,
    UserRepo,
)
from src.interface.api.schemas.scheduling_schemas import (
    CancellationResultResponse,
    CancelSchedulingRequest,
    CreateReviewRequest,
    CreateSchedulingRequest,
    ReviewResponse,
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
    user_repo: UserRepo,
    instructor_repo: InstructorRepo,
) -> SchedulingResponse:
    """Solicita um novo agendamento de aula."""
    use_case = CreateSchedulingUseCase(
        user_repository=user_repo,
        instructor_repository=instructor_repo,
        scheduling_repository=scheduling_repo,
        availability_repository=availability_repo,
    )

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
    status_filter: str | None = Query(None, description="Filter by status (comma-separated, e.g. 'completed,cancelled')"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
) -> SchedulingListResponse:
    """Lista agendamentos do aluno."""
    # Parse multiple statuses if provided
    statuses = None
    if status_filter:
        try:
            statuses = [SchedulingStatus(s.strip()) for s in status_filter.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status in filter: {status_filter}",
            )

    offset = (page - 1) * limit
    schedulings = await scheduling_repo.list_by_student(
        student_id=current_user.id,
        status=statuses,
        limit=limit,
        offset=offset,
    )
    total = await scheduling_repo.count_by_student(
        student_id=current_user.id,
        status=statuses,
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


@router.post(
    "/{scheduling_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Avaliar aula",
    description="Adiciona uma avaliação para uma aula concluída.",
)
async def evaluate_lesson(
    scheduling_id: UUID,
    request: CreateReviewRequest,
    current_user: CurrentStudent,
    review_repo: ReviewRepo,
    scheduling_repo: SchedulingRepo,
    instructor_repo: InstructorRepo,
) -> ReviewResponse:
    """Adiciona uma avaliação para uma aula concluída."""
    use_case = CreateReviewUseCase(
        review_repo=review_repo,
        scheduling_repo=scheduling_repo,
        instructor_repo=instructor_repo,
    )

    try:
        result = await use_case.execute(
            scheduling_id=scheduling_id,
            student_id=current_user.id,
            rating=request.rating,
            comment=request.comment,
        )
        return ReviewResponse.model_validate(result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
