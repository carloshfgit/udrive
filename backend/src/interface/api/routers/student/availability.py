"""
Student Availability Router

Endpoints para alunos consultarem disponibilidade de instrutores.
"""

from datetime import date, datetime, time, timedelta
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.domain.exceptions import InstructorNotFoundException, UserNotFoundException
from src.interface.api.dependencies import (
    AvailabilityRepo,
    CurrentStudent,
    InstructorRepo,
    SchedulingRepo,
    UserRepo,
)
from src.interface.api.schemas.scheduling_schemas import (
    AvailabilityListResponse,
    AvailabilityResponse,
    AvailableTimeSlotsResponse,
    TimeSlotResponse,
)

router = APIRouter(prefix="/instructors", tags=["Student - Instructor Availability"])


@router.get(
    "/{instructor_id}/availability",
    response_model=AvailabilityListResponse,
    summary="Listar disponibilidade do instrutor",
    description="Retorna os slots de disponibilidade configurados pelo instrutor.",
)
async def get_instructor_availability(
    instructor_id: UUID,
    current_user: CurrentStudent,
    availability_repo: AvailabilityRepo,
    user_repo: UserRepo,
) -> AvailabilityListResponse:
    """
    Lista a disponibilidade semanal configurada pelo instrutor.
    
    Retorna apenas slots ativos.
    """
    # Verificar se instrutor existe
    instructor = await user_repo.get_by_id(instructor_id)
    if instructor is None or not instructor.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrutor não encontrado",
        )

    # Buscar slots ativos
    availabilities = await availability_repo.list_by_instructor(
        instructor_id=instructor_id,
        only_active=True,
    )

    return AvailabilityListResponse(
        availabilities=[
            AvailabilityResponse(
                id=a.id,
                instructor_id=a.instructor_id,
                day_of_week=a.day_of_week,
                day_name=a.day_name,
                start_time=a.start_time.strftime("%H:%M"),
                end_time=a.end_time.strftime("%H:%M"),
                is_active=a.is_active,
                duration_minutes=a.duration_minutes,
            )
            for a in availabilities
        ],
        instructor_id=instructor_id,
        total_count=len(availabilities),
    )


@router.get(
    "/{instructor_id}/available-slots",
    response_model=AvailableTimeSlotsResponse,
    summary="Buscar horários disponíveis para uma data",
    description="Retorna os horários livres para agendamento em uma data específica.",
)
async def get_available_time_slots(
    instructor_id: UUID,
    current_user: CurrentStudent,
    availability_repo: AvailabilityRepo,
    scheduling_repo: SchedulingRepo,
    user_repo: UserRepo,
    instructor_repo: InstructorRepo,
    target_date: date = Query(..., description="Data para consulta (YYYY-MM-DD)"),
    duration_minutes: int = Query(60, ge=30, le=120, description="Duração da aula em minutos"),
) -> AvailableTimeSlotsResponse:
    """
    Busca horários livres para agendamento.
    
    1. Verifica disponibilidade configurada para o dia da semana
    2. Exclui horários que já possuem agendamentos
    3. Exclui horários no passado (se for hoje)
    """
    # Verificar se instrutor existe
    instructor = await user_repo.get_by_id(instructor_id)
    if instructor is None or not instructor.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrutor não encontrado",
        )

    # Verificar se instrutor está disponível
    instructor_profile = await instructor_repo.get_by_user_id(instructor_id)
    if instructor_profile is None or not instructor_profile.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instrutor não está aceitando novos alunos no momento",
        )

    # Não permitir datas passadas
    today = date.today()
    if target_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível consultar datas passadas",
        )

    # Converter data para dia da semana (0=Segunda, 6=Domingo)
    # Python weekday(): 0=Monday, 6=Sunday - já está no padrão correto
    day_of_week = target_date.weekday()

    # Buscar slots configurados para este dia da semana
    day_availabilities = await availability_repo.get_by_instructor_and_day(
        instructor_id=instructor_id,
        day_of_week=day_of_week,
        only_active=True,
    )

    if not day_availabilities:
        return AvailableTimeSlotsResponse(
            instructor_id=instructor_id,
            date=target_date.isoformat(),
            time_slots=[],
            total_available=0,
        )

    # Gerar slots de horário baseados na disponibilidade
    time_slots: list[TimeSlotResponse] = []
    now = datetime.now()

    for availability in day_availabilities:
        # Gerar slots de hora em hora dentro do período de disponibilidade
        current_time = availability.start_time
        slot_duration = timedelta(minutes=duration_minutes)

        while True:
            # Calcular fim do slot
            slot_start_dt = datetime.combine(target_date, current_time)
            slot_end_dt = slot_start_dt + slot_duration
            slot_end_time = slot_end_dt.time()

            # Verificar se ainda está dentro da disponibilidade
            if slot_end_time > availability.end_time:
                break

            # Verificar se não é horário passado (se for hoje)
            is_past = target_date == today and slot_start_dt <= now

            # Verificar conflito com agendamentos existentes
            has_conflict = await scheduling_repo.check_conflict(
                instructor_id=instructor_id,
                scheduled_datetime=slot_start_dt,
                duration_minutes=duration_minutes,
            )

            is_available = not is_past and not has_conflict

            time_slots.append(
                TimeSlotResponse(
                    start_time=current_time.strftime("%H:%M"),
                    end_time=slot_end_time.strftime("%H:%M"),
                    is_available=is_available,
                )
            )

            # Avançar para próximo slot (de hora em hora)
            current_time = (datetime.combine(target_date, current_time) + timedelta(hours=1)).time()

    # Contar disponíveis
    available_count = sum(1 for slot in time_slots if slot.is_available)

    return AvailableTimeSlotsResponse(
        instructor_id=instructor_id,
        date=target_date.isoformat(),
        time_slots=time_slots,
        total_available=available_count,
    )
