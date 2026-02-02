"""
Scheduling Router

Definição dos endpoints para gerenciamento de agendamentos e disponibilidade.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.scheduling_dtos import (
    CancelSchedulingDTO,
    ConfirmSchedulingDTO,
    CreateAvailabilityDTO,
    CreateSchedulingDTO,
)
from src.application.use_cases.scheduling.cancel_scheduling import CancelSchedulingUseCase
from src.application.use_cases.scheduling.complete_scheduling import (
    CompleteSchedulingUseCase,
)
from src.application.use_cases.scheduling.confirm_scheduling import (
    ConfirmSchedulingUseCase,
)
from src.application.use_cases.scheduling.create_scheduling import CreateSchedulingUseCase
from src.application.use_cases.scheduling.list_user_schedulings import (
    ListUserSchedulingsUseCase,
)
from src.application.use_cases.scheduling.manage_availability import (
    ManageAvailabilityUseCase,
)
from src.domain.entities.scheduling_status import SchedulingStatus
from src.interface.api.dependencies import (
    AvailabilityRepo,
    CurrentInstructor,
    CurrentStudent,
    CurrentUser,
    SchedulingRepo,
)
from src.interface.api.schemas.scheduling_schemas import (
    AvailabilityListResponse,
    AvailabilityResponse,
    CancellationResultResponse,
    CancelSchedulingRequest,
    CreateAvailabilityRequest,
    CreateSchedulingRequest,
    SchedulingListResponse,
    SchedulingResponse,
    UpdateAvailabilityRequest,
)

router = APIRouter(prefix="/schedulings", tags=["Schedulings"])
availability_router = APIRouter(prefix="/availability", tags=["Availability"])
instructor_availability_router = APIRouter(prefix="/instructors", tags=["Availability"])


# =============================================================================
# Scheduling Endpoints
# =============================================================================

@router.post(
    "",
    response_model=SchedulingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo agendamento",
)
async def create_scheduling(
    request: CreateSchedulingRequest,
    current_user: CurrentStudent,
    scheduling_repo: SchedulingRepo,
    availability_repo: AvailabilityRepo,
) -> SchedulingResponse:
    """Solicita um novo agendamento de aula."""
    use_case = CreateSchedulingUseCase(scheduling_repo, availability_repo)
    input_dto = CreateSchedulingDTO(
        student_id=current_user.id,
        instructor_id=request.instructor_id,
        scheduled_datetime=request.scheduled_datetime,
        duration_minutes=request.duration_minutes,
    )
    result = await use_case.execute(input_dto)
    return SchedulingResponse.model_validate(result)


@router.get(
    "",
    response_model=SchedulingListResponse,
    summary="Listar agendamentos do usuário",
)
async def list_schedulings(
    current_user: CurrentUser,
    scheduling_repo: SchedulingRepo,
    status: SchedulingStatus | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
) -> SchedulingListResponse:
    """Lista agendamentos do usuário atual (aluno ou instrutor)."""
    use_case = ListUserSchedulingsUseCase(scheduling_repo)
    result = await use_case.execute(
        user_id=current_user.id,
        status=status,
        limit=limit,
        offset=(page - 1) * limit,
    )
    
    # Map DTO to Schema
    return SchedulingListResponse(
        schedulings=[SchedulingResponse.model_validate(s) for s in result.items],
        total_count=result.total,
        limit=result.limit,
        offset=result.offset,
        has_more=(result.offset + result.limit) < result.total,
    )


@router.get(
    "/{scheduling_id}",
    response_model=SchedulingResponse,
    summary="Obter detalhes do agendamento",
)
async def get_scheduling(
    scheduling_id: UUID,
    current_user: CurrentUser,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse:
    """Obtém detalhes de um agendamento específico."""
    # Como não temos um use case específico apenas para GET (apenas List),
    # podemos usar o repositório diretamente ou criar um use case GetSchedulingDetail.
    # Por simplicidade e Clean Arch, ideal é Use Case, mas GetById é trivial.
    # Vamos usar o repo com verificação de permissão.
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if not scheduling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado"
        )
    
    if scheduling.student_id != current_user.id and scheduling.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado"
        )
        
    return SchedulingResponse.model_validate(scheduling)


@router.post(
    "/{scheduling_id}/cancel",
    response_model=CancellationResultResponse,
    summary="Cancelar agendamento",
)
async def cancel_scheduling(
    scheduling_id: UUID,
    request: CancelSchedulingRequest,
    current_user: CurrentUser,
    scheduling_repo: SchedulingRepo,
) -> CancellationResultResponse:
    """Cancela um agendamento."""
    use_case = CancelSchedulingUseCase(scheduling_repo)
    input_dto = CancelSchedulingDTO(
        scheduling_id=scheduling_id,
        cancelled_by=current_user.id,
        reason=request.reason,
    )
    result = await use_case.execute(input_dto)
    
    return CancellationResultResponse(
        scheduling_id=result.scheduling_id,
        status=result.status.value,
        refund_percentage=int(result.refund_percentage * 100),
        refund_amount=result.refund_amount,
        message=f"Agendamento cancelado. Reembolso de {int(result.refund_percentage * 100)}% aplicado.",
    )


@router.post(
    "/{scheduling_id}/confirm",
    response_model=SchedulingResponse,
    summary="Confirmar agendamento (Instrutor)",
)
async def confirm_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse:
    """Confirma um agendamento pendente."""
    use_case = ConfirmSchedulingUseCase(scheduling_repo)
    input_dto = ConfirmSchedulingDTO(
        scheduling_id=scheduling_id,
        instructor_id=current_user.id,
    )
    result = await use_case.execute(input_dto)
    return SchedulingResponse.model_validate(result)


@router.post(
    "/{scheduling_id}/complete",
    response_model=SchedulingResponse,
    summary="Concluir agendamento (Sistema/Instrutor)",
)
async def complete_scheduling(
    scheduling_id: UUID,
    current_user: CurrentInstructor,
    scheduling_repo: SchedulingRepo,
) -> SchedulingResponse:
    """Marca um agendamento como concluído."""
    # Idealmente chamado automaticamente ou pelo instrutor
    use_case = CompleteSchedulingUseCase(scheduling_repo)
    # Por enquanto, permitimos que o instrutor marque, ou admin.
    # Verificação de permissão está dentro do use case?
    # O use case CompleteSchedulingUseCase atualmente recebe scheduling_id.
    # Vamos adaptar para receber user_id se necessário, ou assumir validação prévia.
    # Olhando o use case: ele apenas pega pelo ID e verifica se está CONFIRMED e se data já passou.
    # Não valida quem está chamando explicitamente no execute (deveria).
    # Vamos adicionar verificação aqui: só instrutor do agendamento.
    
    scheduling = await scheduling_repo.get_by_id(scheduling_id)
    if not scheduling:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    if scheduling.instructor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Apenas o instrutor pode concluir")

    result = await use_case.execute(scheduling_id)
    return SchedulingResponse.model_validate(result)


# =============================================================================
# Availability Endpoints
# =============================================================================

@availability_router.post(
    "",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar slot de disponibilidade",
)
async def create_availability(
    request: CreateAvailabilityRequest,
    current_user: CurrentInstructor,
    availability_repo: AvailabilityRepo,
) -> AvailabilityResponse:
    """Cria um novo horário disponível para o instrutor."""
    use_case = ManageAvailabilityUseCase(availability_repo)
    
    # Conversão de string HH:MM para time object
    from datetime import datetime
    try:
        start_time = datetime.strptime(request.start_time, "%H:%M").time()
        end_time = datetime.strptime(request.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM")

    input_dto = CreateAvailabilityDTO(
        instructor_id=current_user.id,
        day_of_week=request.day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    result = await use_case.create_slot(input_dto)
    return AvailabilityResponse.model_validate(result)


@availability_router.delete(
    "/{availability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover slot de disponibilidade",
)
async def delete_availability(
    availability_id: UUID,
    current_user: CurrentInstructor,
    availability_repo: AvailabilityRepo,
) -> None:
    """Remove um slot de disponibilidade."""
    use_case = ManageAvailabilityUseCase(availability_repo)
    await use_case.delete_slot(availability_id, current_user.id)


@instructor_availability_router.get(
    "/{instructor_id}/availability",
    response_model=AvailabilityListResponse,
    summary="Listar disponibilidade pública do instrutor",
)
async def list_instructor_availability(
    instructor_id: UUID,
    availability_repo: AvailabilityRepo,
) -> AvailabilityListResponse:
    """Lista horários disponíveis de um instrutor."""
    # Usando o repo diretamente para leitura pública
    slots = await availability_repo.list_by_instructor(instructor_id, only_active=True)
    
    response_items = []
    days_map = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}
    
    for slot in slots:
        # Calcular duração em minutos
        from datetime import datetime, date
        dummy_date = date.today()
        dt_start = datetime.combine(dummy_date, slot.start_time)
        dt_end = datetime.combine(dummy_date, slot.end_time)
        duration = (dt_end - dt_start).total_seconds() / 60
        
        response_items.append(AvailabilityResponse(
            id=slot.id,
            instructor_id=slot.instructor_id,
            day_of_week=slot.day_of_week,
            day_name=days_map.get(slot.day_of_week, "Desconhecido"),
            start_time=slot.start_time.strftime("%H:%M"),
            end_time=slot.end_time.strftime("%H:%M"),
            is_active=slot.is_active,
            duration_minutes=int(duration)
        ))

    return AvailabilityListResponse(
        availabilities=response_items,
        instructor_id=instructor_id,
        total_count=len(response_items)
    )
