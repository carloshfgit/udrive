"""
Instructor Profile Router

Endpoints para gerenciamento de perfil de instrutores.
"""

from fastapi import APIRouter, HTTPException, status

from src.application.dtos.profile_dtos import UpdateInstructorProfileDTO, UpdateLocationDTO
from src.application.use_cases.instructor.update_instructor_location import (
    UpdateInstructorLocationUseCase,
)
from src.application.use_cases.instructor.update_instructor_profile import (
    UpdateInstructorProfileUseCase,
)
from src.domain.exceptions import (
    InstructorNotFoundException,
    InvalidLocationException,
)
from src.interface.api.schemas.profiles import (
    InstructorProfileResponse,
    LocationResponse,
    UpdateInstructorProfileRequest,
    UpdateLocationRequest,
)
from src.interface.api.dependencies import (
    CurrentInstructor,
    InstructorRepo,
    ReviewRepo,
    UserRepo,
)
from src.interface.api.schemas.reviews import InstructorReviewsListResponse, InstructorReviewResponse

router = APIRouter(tags=["Instructor - Profile"])


@router.get(
    "/profile",
    response_model=InstructorProfileResponse,
    summary="Obter perfil do instrutor atual",
    description="Retorna os dados do perfil do instrutor autenticado.",
)
async def get_current_instructor_profile(
    current_user: CurrentInstructor,
    instructor_repo: InstructorRepo,
) -> InstructorProfileResponse:
    """Retorna o perfil do instrutor logado."""
    profile = await instructor_repo.get_by_user_id(current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de instrutor não encontrado",
        )

    return InstructorProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        city=profile.city,
        vehicle_type=profile.vehicle_type,
        license_category=profile.license_category,
        hourly_rate=profile.hourly_rate,
        rating=profile.rating,
        total_reviews=profile.total_reviews,
        is_available=profile.is_available,
        full_name=current_user.full_name,
        phone=current_user.phone,
        cpf=current_user.cpf,
        birth_date=current_user.birth_date,
        biological_sex=current_user.biological_sex,
        location=LocationResponse.model_validate(profile.location) if profile.location else None,
        has_mp_account=profile.has_mp_account,
        price_cat_a_instructor_vehicle=profile.price_cat_a_instructor_vehicle,
        price_cat_a_student_vehicle=profile.price_cat_a_student_vehicle,
        price_cat_b_instructor_vehicle=profile.price_cat_b_instructor_vehicle,
        price_cat_b_student_vehicle=profile.price_cat_b_student_vehicle,
    )


@router.put(
    "/profile",
    response_model=InstructorProfileResponse,
    summary="Criar ou atualizar perfil",
    description="Cria ou atualiza o perfil do instrutor autenticado.",
)
async def update_instructor_profile(
    request: UpdateInstructorProfileRequest,
    current_user: CurrentInstructor,
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
        city=request.city,
        vehicle_type=request.vehicle_type,
        license_category=request.license_category,
        hourly_rate=request.hourly_rate,
        is_available=request.is_available,
        full_name=request.full_name,
        phone=request.phone,
        cpf=request.cpf,
        birth_date=request.birth_date,
        biological_sex=request.biological_sex,
        latitude=request.latitude,
        longitude=request.longitude,
        price_cat_a_instructor_vehicle=request.price_cat_a_instructor_vehicle,
        price_cat_a_student_vehicle=request.price_cat_a_student_vehicle,
        price_cat_b_instructor_vehicle=request.price_cat_b_instructor_vehicle,
        price_cat_b_student_vehicle=request.price_cat_b_student_vehicle,
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
    description="Atualiza a localização geográfica do instrutor.",
)
async def update_location(
    request: UpdateLocationRequest,
    current_user: CurrentInstructor,
    instructor_repo: InstructorRepo,
) -> None:
    """Atualiza localização do instrutor."""
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
    "/profile/reviews",
    response_model=InstructorReviewsListResponse,
    summary="Obter avaliações do instrutor atual",
    description="Retorna a nota média e os comentários dos alunos para o instrutor autenticado.",
)
async def get_current_instructor_reviews(
    current_user: CurrentInstructor,
    instructor_repo: InstructorRepo,
    review_repo: ReviewRepo,
) -> InstructorReviewsListResponse:
    """Retorna as avaliações do instrutor logado."""
    profile = await instructor_repo.get_by_user_id(current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de instrutor não encontrado",
        )

    reviews = await review_repo.get_by_instructor_id_with_student(current_user.id)

    # Filtrar para ter o mesmo comportamento do endpoint público (uma avaliação por aluno)
    best_reviews = {}
    for r in reviews:
        student_id = r.student_id
        if student_id not in best_reviews:
            best_reviews[student_id] = r
        else:
            current_best = best_reviews[student_id]
            current_has_comment = bool(current_best.comment and current_best.comment.strip())
            new_has_comment = bool(r.comment and r.comment.strip())
            if not current_has_comment and new_has_comment:
                best_reviews[student_id] = r

    return InstructorReviewsListResponse(
        rating=float(profile.rating),
        total_reviews=profile.total_reviews,
        reviews=[
            InstructorReviewResponse(
                id=r.id,
                rating=r.rating,
                comment=r.comment,
                student_name=r.student_name or "Aluno",
                created_at=r.created_at,
            )
            for r in best_reviews.values()
        ],
    )
