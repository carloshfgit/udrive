"""
Shared Instructors Router

Endpoints públicos/compartilhados relacionados a instrutores.
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from src.interface.api.dependencies import AvailabilityRepo, InstructorRepo, UserRepo
from src.interface.api.schemas.scheduling_schemas import AvailabilityListResponse, AvailabilityResponse

router = APIRouter(prefix="/instructors", tags=["Shared - Instructors"])

DAYS_MAP = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo",
}


# === Schemas ===

class LocationData(BaseModel):
    """Dados de localização."""
    latitude: float
    longitude: float


class InstructorDetailResponse(BaseModel):
    """Schema de resposta para detalhes do instrutor."""
    id: str
    user_id: str
    name: str
    bio: str
    vehicle_type: str
    license_category: str
    hourly_rate: float
    rating: float
    total_reviews: int
    is_available: bool
    location: LocationData | None = None


# === Endpoints ===

@router.get(
    "/{instructor_id}/availability",
    response_model=AvailabilityListResponse,
    summary="Listar disponibilidade do instrutor",
    description="Lista horários disponíveis de um instrutor específico.",
)
async def list_instructor_availability(
    instructor_id: UUID,
    availability_repo: AvailabilityRepo,
    only_active: bool = Query(True, description="Apenas slots ativos"),
) -> AvailabilityListResponse:
    """Lista horários disponíveis de um instrutor."""
    slots = await availability_repo.list_by_instructor(instructor_id, only_active=only_active)

    response_items = []
    for slot in slots:
        # Calcular duração em minutos
        dummy_date = date.today()
        dt_start = datetime.combine(dummy_date, slot.start_time)
        dt_end = datetime.combine(dummy_date, slot.end_time)
        duration = int((dt_end - dt_start).total_seconds() / 60)

        response_items.append(
            AvailabilityResponse(
                id=slot.id,
                instructor_id=slot.instructor_id,
                day_of_week=slot.day_of_week,
                day_name=DAYS_MAP.get(slot.day_of_week, "Desconhecido"),
                start_time=slot.start_time.strftime("%H:%M"),
                end_time=slot.end_time.strftime("%H:%M"),
                is_active=slot.is_active,
                duration_minutes=duration,
            )
        )

    return AvailabilityListResponse(
        availabilities=response_items,
        instructor_id=instructor_id,
        total_count=len(response_items),
    )


@router.get(
    "/{instructor_id}",
    response_model=InstructorDetailResponse,
    summary="Obter detalhes do instrutor",
    description="Obtém informações públicas de um instrutor específico.",
)
async def get_instructor_by_id(
    instructor_id: UUID,
    instructor_repo: InstructorRepo,
    user_repo: UserRepo,
) -> InstructorDetailResponse:
    """Obtém detalhes públicos de um instrutor."""
    instructor = await instructor_repo.get_by_user_id(instructor_id)
    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrutor não encontrado",
        )

    # Buscar nome do usuário
    user = await user_repo.get_by_id(instructor_id)
    user_name = user.full_name if user else "Instrutor"

    location = None
    if instructor.latitude and instructor.longitude:
        location = LocationData(
            latitude=instructor.latitude,
            longitude=instructor.longitude,
        )

    return InstructorDetailResponse(
        id=str(instructor.id),
        user_id=str(instructor.user_id),
        name=user_name,
        bio=instructor.bio or "",
        vehicle_type=instructor.vehicle_type or "",
        license_category=instructor.license_category or "",
        hourly_rate=float(instructor.hourly_rate),
        rating=float(instructor.rating),
        total_reviews=instructor.total_reviews,
        is_available=instructor.is_available,
        location=location,
    )
