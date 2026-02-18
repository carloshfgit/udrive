"""
Shared Instructors Router

Endpoints públicos/compartilhados relacionados a instrutores.
"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from src.interface.api.dependencies import AvailabilityRepo, InstructorRepo, ReviewRepo
from src.interface.api.schemas.scheduling_schemas import AvailabilityListResponse, AvailabilityResponse
from src.infrastructure.services.pricing_service import PricingService

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


class PublicReviewResponse(BaseModel):
    """Schema de resposta para uma avaliação pública."""
    rating: int
    comment: str | None
    student_name: str
    created_at: datetime


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
    reviews: list[PublicReviewResponse] = []


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
    review_repo: ReviewRepo,
) -> InstructorDetailResponse:
    """Obtém detalhes públicos de um instrutor."""
    instructor = await instructor_repo.get_public_profile_by_user_id(instructor_id)
    if instructor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrutor não encontrado",
        )

    user_name = instructor.full_name or "Instrutor"

    location = None
    if instructor.location:
        location = LocationData(
            latitude=instructor.location.latitude,
            longitude=instructor.location.longitude,
        )

    # Buscar avaliações
    all_reviews = await review_repo.get_by_instructor_id_with_student(instructor_id)
    
    # Filtrar: manter apenas uma avaliação por aluno
    # Regra: selecionar a mais antiga que possua comentário. 
    # Se nenhuma tiver comentário, selecionar a primeira realizada.
    # Como all_reviews já está ordenado por created_at ASC, a primeira encontrada de cada aluno
    # é a "reserva" inicial, que é substituída apenas se encontrarmos uma posterior com comentário 
    # (ou se a primeira já for a com comentário).
    best_reviews = {}
    
    for r in all_reviews:
        student_id = r.student_id
        if student_id not in best_reviews:
            best_reviews[student_id] = r
        else:
            # Já temos uma reserva. Se ela não tem comentário e a atual tem, substituímos.
            current_best = best_reviews[student_id]
            current_has_comment = bool(current_best.comment and current_best.comment.strip())
            new_has_comment = bool(r.comment and r.comment.strip())
            
            if not current_has_comment and new_has_comment:
                best_reviews[student_id] = r

    filtered_reviews = [
        PublicReviewResponse(
            rating=r.rating,
            comment=r.comment,
            student_name=r.student_name or "Aluno",
            created_at=r.created_at,
        )
        for r in best_reviews.values()
    ]

    return InstructorDetailResponse(
        id=str(instructor.id),
        user_id=str(instructor.user_id),
        name=user_name,
        bio=instructor.bio or "",
        vehicle_type=instructor.vehicle_type or "",
        license_category=instructor.license_category or "",
        hourly_rate=float(PricingService.calculate_final_price(instructor.hourly_rate)),
        rating=float(instructor.rating),
        total_reviews=instructor.total_reviews,
        is_available=instructor.is_available,
        location=location,
        reviews=filtered_reviews,
    )
