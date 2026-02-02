"""
Instructor Availability Router

Endpoints para gerenciamento de disponibilidade do instrutor.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.application.dtos.scheduling_dtos import CreateAvailabilityDTO
from src.application.use_cases.scheduling import ManageAvailabilityUseCase
from src.interface.api.dependencies import AvailabilityRepo, CurrentInstructor, UserRepo
from src.interface.api.schemas.scheduling_schemas import (
    AvailabilityResponse,
    CreateAvailabilityRequest,
)

router = APIRouter(prefix="/availability", tags=["Instructor - Availability"])


@router.post(
    "",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar disponibilidade",
    description="Cria um novo horário disponível para o instrutor.",
)
async def create_availability(
    request: CreateAvailabilityRequest,
    current_user: CurrentInstructor,
    availability_repo: AvailabilityRepo,
    user_repo: UserRepo,
) -> AvailabilityResponse:
    """Cria um novo horário disponível para o instrutor."""
    use_case = ManageAvailabilityUseCase(
        availability_repository=availability_repo,
        user_repository=user_repo,
    )

    # Conversão de string HH:MM para time object
    try:
        start_time = datetime.strptime(request.start_time, "%H:%M").time()
        end_time = datetime.strptime(request.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de hora inválido. Use HH:MM",
        )

    dto = CreateAvailabilityDTO(
        instructor_id=current_user.id,
        day_of_week=request.day_of_week,
        start_time=start_time,
        end_time=end_time,
    )

    result = await use_case.create(dto)
    return AvailabilityResponse.model_validate(result)


@router.delete(
    "/{availability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover disponibilidade",
    description="Remove um slot de disponibilidade.",
)
async def delete_availability(
    availability_id: UUID,
    current_user: CurrentInstructor,
    availability_repo: AvailabilityRepo,
) -> None:
    """Remove um slot de disponibilidade."""
    availability = await availability_repo.get_by_id(availability_id)
    if availability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disponibilidade não encontrada",
        )

    if availability.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado",
        )

    await availability_repo.delete(availability_id)
