"""
Instructor Router

Endpoints para gerenciamento de perfil de instrutores e busca por localização.
"""

from fastapi import APIRouter, HTTPException, status

from src.application.dtos.profile_dtos import (
    InstructorSearchDTO,
    UpdateInstructorProfileDTO,
    UpdateLocationDTO,
)
from src.application.use_cases.get_nearby_instructors import GetNearbyInstructorsUseCase
from src.application.use_cases.update_instructor_location import (
    UpdateInstructorLocationUseCase,
)
from src.application.use_cases.update_instructor_profile import (
    UpdateInstructorProfileUseCase,
)
from src.domain.exceptions import InstructorNotFoundException, InvalidLocationException
from src.interface.api.dependencies import (
    CurrentUser,
    InstructorRepo,
    LocationService,
    UserRepo,
)
from src.interface.api.schemas.profiles import (
    InstructorProfileResponse,
    InstructorSearchResponse,
    UpdateInstructorProfileRequest,
    UpdateLocationRequest,
)

router = APIRouter(prefix="/instructors", tags=["Instructors"])


@router.get(
    "/profile",
    response_model=InstructorProfileResponse,
    summary="Obter perfil do instrutor atual",
    description="Retorna os dados do perfil do instrutor autenticado.",
)
async def get_current_instructor_profile(
    current_user: CurrentUser,
    instructor_repo: InstructorRepo,
) -> InstructorProfileResponse:
    """Retorna o perfil do instrutor logado."""
    profile = await instructor_repo.get_by_user_id(current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de instrutor não encontrado",
        )

    # Conversão manual rápida pois o ResponseModel fará a validação final
    # Para produção idealmente teríamos um mapper
    return InstructorProfileResponse.model_validate(profile)


@router.put(
    "/profile",
    response_model=InstructorProfileResponse,
    summary="Criar ou atualizar perfil",
    description="Cria ou atualiza o perfil do instrutor autenticado.",
)
async def update_instructor_profile(
    request: UpdateInstructorProfileRequest,
    current_user: CurrentUser,
    user_repo: UserRepo,
    instructor_repo: InstructorRepo,
) -> InstructorProfileResponse:
    """Atualiza perfil do instrutor."""
    use_case = UpdateInstructorProfileUseCase(
        user_repository=user_repo,
        instructor_repository=instructor_repo,
    )

    dto = UpdateInstructorProfileDTO(
        user_id=current_user.id,
        bio=request.bio,
        vehicle_type=request.vehicle_type,
        license_category=request.license_category,
        hourly_rate=request.hourly_rate,
        is_available=request.is_available,
    )

    try:
        result = await use_case.execute(dto)
        return InstructorProfileResponse.model_validate(result)
    except InstructorNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar perfil",
        ) from e


@router.put(
    "/location",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar localização",
    description="Atualiza a localização geográfica do instrutor (otimizado).",
)
async def update_location(
    request: UpdateLocationRequest,
    current_user: CurrentUser,
    instructor_repo: InstructorRepo,
) -> None:
    """
    Atualiza localização do instrutor.
    Retorna 204 No Content em sucesso.
    """
    use_case = UpdateInstructorLocationUseCase(
        instructor_repository=instructor_repo,
    )

    dto = UpdateLocationDTO(
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    try:
        await use_case.execute(dto)
    except InvalidLocationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except InstructorNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


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
    radius_km: float = 10.0,
    limit: int = 50,
    # TODO: Injetar CacheService aqui quando disponível
) -> InstructorSearchResponse:
    """Busca instrutores por proximidade."""
    # Nota: Usamos GetNearbyInstructorsUseCase que suporta cache
    # Por enquanto, passamos cache_service=None
    use_case = GetNearbyInstructorsUseCase(
        instructor_repository=instructor_repo,
        cache_service=None,  # Injetar quando tivermos o provider
    )

    dto = InstructorSearchDTO(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        only_available=True,  # Default: apenas disponíveis
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
