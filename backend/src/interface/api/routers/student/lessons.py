"""
Student Lessons Router

Endpoints para gerenciamento de agendamentos do aluno.
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException, Query, status

from src.application.dtos.scheduling_dtos import (
    CancelSchedulingDTO,
    CompleteSchedulingDTO,
    CreateSchedulingDTO,
    RequestRescheduleDTO,
    RespondRescheduleDTO,
    StartSchedulingDTO,
)
from src.application.use_cases.create_review_use_case import CreateReviewUseCase
from src.application.use_cases.scheduling import (
    CancelSchedulingUseCase,
    CompleteSchedulingUseCase,
    CreateSchedulingUseCase,
    GetNextStudentSchedulingUseCase,
    RequestRescheduleUseCase,
    RespondRescheduleUseCase,
    StartSchedulingUseCase,
)
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
    RequestRescheduleRequest,
    RespondRescheduleRequest,
    ReviewResponse,
    SchedulingListResponse,
    SchedulingResponse,
)
from src.interface.websockets.event_dispatcher import get_event_dispatcher

logger = structlog.get_logger()

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

    # Emitir evento em tempo real para o instrutor
    dispatcher = get_event_dispatcher()
    if dispatcher:
        try:
            await dispatcher.emit_scheduling_created(result)
        except Exception as e:
            logger.error("event_dispatch_error", dispatch_event="scheduling_created", error=str(e))

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
    "/next",
    response_model=SchedulingResponse | None,
    summary="Obter próxima aula",
    description="Busca a próxima aula confirmada ou pendente do aluno.",
)
async def get_next_student_lesson(
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse | None:
    """Busca a próxima aula do aluno."""
    use_case = GetNextStudentSchedulingUseCase(scheduling_repo)
    result = await use_case.execute(current_user.id)
    
    if result is None:
        return None
        
    return SchedulingResponse.model_validate(result)


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
    "/{scheduling_id}/request-reschedule",
    response_model=SchedulingResponse,
    summary="Solicitar reagendamento",
    description="Solicita uma nova data/horário para uma aula.",
)
async def request_reschedule(
    scheduling_id: UUID,
    request: RequestRescheduleRequest,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    availability_repo: AvailabilityRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Solicita reagendamento de aula."""
    use_case = RequestRescheduleUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
        availability_repository=availability_repo,
    )

    dto = RequestRescheduleDTO(
        scheduling_id=scheduling_id,
        user_id=current_user.id,
        new_datetime=request.new_datetime,
    )

    try:
        result = await use_case.execute(dto)

        # Emitir evento em tempo real para o instrutor
        dispatcher = get_event_dispatcher()
        if dispatcher:
            try:
                await dispatcher.emit_reschedule_requested(result)
            except Exception as e:
                logger.error("event_dispatch_error", dispatch_event="reschedule_requested", error=str(e))

        return SchedulingResponse.model_validate(result)
    except (ValueError, Exception) as e:
        # Note: exceptions should ideally be handled by a global handler 
        # but following local pattern if any or just raising.
        # Actually some routers handle exceptions explicitly.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{scheduling_id}/respond-reschedule",
    response_model=SchedulingResponse,
    summary="Responder a reagendamento",
    description="Aceita ou recusa uma solicitação de reagendamento (ação do aluno).",
)
async def respond_reschedule(
    scheduling_id: UUID,
    request: RespondRescheduleRequest,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Aceita ou recusa uma solicitação de reagendamento."""
    use_case = RespondRescheduleUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
    )

    dto = RespondRescheduleDTO(
        scheduling_id=scheduling_id,
        user_id=current_user.id,
        accepted=request.accepted,
    )

    try:
        result = await use_case.execute(dto)

        # Emitir evento em tempo real para o instrutor
        dispatcher = get_event_dispatcher()
        if dispatcher:
            try:
                await dispatcher.emit_reschedule_responded(result, request.accepted)
            except Exception as e:
                logger.error("event_dispatch_error", dispatch_event="reschedule_responded", error=str(e))

        return SchedulingResponse.model_validate(result)
    except (ValueError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{scheduling_id}/start",
    response_model=SchedulingResponse,
    summary="Iniciar aula",
    description="Registra o início da aula.",
)
async def start_lesson(
    scheduling_id: UUID,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Registra o início da aula."""
    use_case = StartSchedulingUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
    )

    dto = StartSchedulingDTO(
        scheduling_id=scheduling_id,
        user_id=current_user.id,
    )

    result = await use_case.execute(dto)

    # Emitir evento em tempo real para a outra parte
    dispatcher = get_event_dispatcher()
    if dispatcher:
        try:
            await dispatcher.emit_scheduling_started(result, current_user.id)
        except Exception as e:
            logger.error("event_dispatch_error", dispatch_event="scheduling_started", error=str(e))

    return SchedulingResponse.model_validate(result)


@router.post(
    "/{scheduling_id}/complete",
    response_model=SchedulingResponse,
    summary="Concluir aula",
    description="Marca a aula como concluída.",
)
async def complete_lesson(
    scheduling_id: UUID,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
) -> SchedulingResponse:
    """Marca a aula como concluída."""
    # Verificar permissão
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if scheduling is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agendamento não encontrado",
        )

    if scheduling.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado",
        )

    use_case = CompleteSchedulingUseCase(scheduling_repo, user_repo)
    dto = CompleteSchedulingDTO(
        scheduling_id=scheduling_id,
        user_id=current_user.id,
        is_student=True,
    )

    result = await use_case.execute(dto)

    # Emitir evento em tempo real para ambas as partes
    dispatcher = get_event_dispatcher()
    if dispatcher:
        try:
            await dispatcher.emit_scheduling_completed(result)
        except Exception as e:
            logger.error("event_dispatch_error", dispatch_event="scheduling_completed", error=str(e))

    return SchedulingResponse.model_validate(result)


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
    user_repo: UserRepo,
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

    use_case = CancelSchedulingUseCase(scheduling_repo, user_repo)
    dto = CancelSchedulingDTO(
        scheduling_id=scheduling_id,
        cancelled_by=current_user.id,
        reason=request.reason,
    )

    result = await use_case.execute(dto)

    # Emitir evento em tempo real para o instrutor
    dispatcher = get_event_dispatcher()
    if dispatcher:
        try:
            # Para cancelamento, precisamos buscar o scheduling completo para obter instructor_id
            scheduling = await scheduling_repo.get_by_id(scheduling_id)
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
                    cancellation_reason=scheduling.cancellation_reason,
                    cancelled_by=scheduling.cancelled_by,
                    cancelled_at=scheduling.cancelled_at,
                )
                await dispatcher.emit_scheduling_cancelled(scheduling_dto, current_user.id)
        except Exception as e:
            logger.error("event_dispatch_error", dispatch_event="scheduling_cancelled", error=str(e))

    return CancellationResultResponse(
        scheduling_id=result.scheduling_id,
        status=result.status,
        refund_percentage=result.refund_percentage,
        refund_amount=result.refund_amount,
        cancelled_at=result.cancelled_at,
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
