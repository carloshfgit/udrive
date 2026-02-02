"""
Student Instructors Router

Endpoints para busca de instrutores (exclusivo para alunos).
"""

from fastapi import APIRouter, HTTPException, status

from src.application.dtos.profile_dtos import InstructorSearchDTO
from src.application.use_cases.student.get_nearby_instructors import (
    GetNearbyInstructorsUseCase,
)
from src.domain.exceptions import InvalidLocationException
from src.interface.api.dependencies import CurrentStudent, InstructorRepo
from src.interface.api.schemas.profiles import InstructorSearchResponse

router = APIRouter(prefix="/instructors", tags=["Student - Instructors"])


@router.get(
    "/search",
    response_model=InstructorSearchResponse,
    summary="Buscar instrutores próximos",
    description="Busca instrutores disponíveis dentro de um raio (km).",
)
async def search_instructors(
    latitude: float,
    longitude: float,
    instructor_repo: InstructorRepo,
    _current_student: CurrentStudent,  # Guard: Apenas alunos podem buscar
    radius_km: float = 10.0,
    limit: int = 50,
) -> InstructorSearchResponse:
    """Busca instrutores por proximidade."""
    use_case = GetNearbyInstructorsUseCase(
        instructor_repository=instructor_repo,
        cache_service=None,
    )

    dto = InstructorSearchDTO(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        only_available=True,
        limit=limit,
    )

    try:
        result = await use_case.execute(dto)
        return InstructorSearchResponse.model_validate(result)
    except InvalidLocationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
