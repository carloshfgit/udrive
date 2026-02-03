"""
Student Profile Router

Endpoints para gerenciamento de perfil de alunos.
"""

from fastapi import APIRouter, HTTPException, status

from src.application.dtos.profile_dtos import UpdateStudentProfileDTO
from src.application.use_cases.student.update_student_profile import (
    UpdateStudentProfileUseCase,
)
from src.domain.exceptions import StudentNotFoundException
from src.interface.api.dependencies import CurrentStudent, StudentRepo, UserRepo
from src.interface.api.schemas.profiles import (
    StudentProfileResponse,
    UpdateStudentProfileRequest,
)

router = APIRouter(tags=["Student - Profile"])


@router.get(
    "/profile",
    response_model=StudentProfileResponse,
    summary="Obter perfil do aluno atual",
    description="Retorna os dados do perfil do aluno autenticado.",
)
async def get_current_student_profile(
    current_user: CurrentStudent,
    student_repo: StudentRepo,
) -> StudentProfileResponse:
    """Retorna o perfil do aluno logado."""
    profile = await student_repo.get_by_user_id(current_user.id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de aluno não encontrado",
        )

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        preferred_schedule=profile.preferred_schedule,
        license_category_goal=profile.license_category_goal,
        learning_stage=profile.learning_stage,
        notes=profile.notes,
        total_lessons=profile.total_lessons,
        phone=current_user.phone or "",
        cpf=current_user.cpf or "",
        birth_date=current_user.birth_date,
        full_name=current_user.full_name or "",
    )


@router.put(
    "/profile",
    response_model=StudentProfileResponse,
    summary="Criar ou atualizar perfil",
    description="Cria ou atualiza o perfil do aluno autenticado.",
)
async def update_student_profile(
    request: UpdateStudentProfileRequest,
    current_user: CurrentStudent,
    user_repo: UserRepo,
    student_repo: StudentRepo,
) -> StudentProfileResponse:
    """Atualiza perfil do aluno."""
    use_case = UpdateStudentProfileUseCase(
        user_repository=user_repo,
        student_repository=student_repo,
    )

    dto = UpdateStudentProfileDTO(
        user_id=current_user.id,
        preferred_schedule=request.preferred_schedule,
        license_category_goal=request.license_category_goal,
        learning_stage=request.learning_stage,
        notes=request.notes,
        phone=request.phone,
        cpf=request.cpf,
        birth_date=request.birth_date,
        full_name=request.full_name,
    )

    try:
        result = await use_case.execute(dto)
        return StudentProfileResponse.model_validate(result)
    except StudentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar perfil",
        ) from e
