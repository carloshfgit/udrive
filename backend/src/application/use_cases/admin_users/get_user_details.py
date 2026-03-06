"""
Get User Details Use Case

Obtém detalhes completos de um usuário para o admin panel.
"""

from uuid import UUID

from src.application.dtos.admin_user_dtos import (
    UserAdminProfileDTO,
    UserAdminResponseDTO,
    UserAdminSchedulingDTO,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.student_repository import IStudentRepository
from src.domain.interfaces.user_repository import IUserRepository


class GetUserDetailsUseCase:
    """Obtém detalhes de um usuário para o painel administrativo."""

    def __init__(
        self,
        user_repository: IUserRepository,
        instructor_repo: IInstructorRepository,
        student_repo: IStudentRepository,
        scheduling_repo: ISchedulingRepository,
    ) -> None:
        self._user_repo = user_repository
        self._instructor_repo = instructor_repo
        self._student_repo = student_repo
        self._scheduling_repo = scheduling_repo

    async def execute(self, user_id: UUID) -> UserAdminResponseDTO | None:
        """Busca detalhes completos de um usuário."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            return None

        # 1. Buscar Perfil e Agendamentos Recentes
        profile_dto = None
        recent_schedulings = []

        if user.is_instructor:
            profile = await self._instructor_repo.get_by_user_id(user_id)
            if profile:
                profile_dto = UserAdminProfileDTO(
                    bio=profile.bio,
                    vehicle_type=profile.vehicle_type,
                    license_category=profile.license_category,
                    hourly_rate=float(profile.hourly_rate),
                    rating=profile.rating,
                    total_reviews=profile.total_reviews,
                )
            # Buscar 5 agendamentos recentes como instrutor
            scheds = await self._scheduling_repo.list_by_instructor(
                instructor_id=user_id, limit=5
            )
            recent_schedulings = [
                UserAdminSchedulingDTO(
                    id=s.id,
                    scheduled_datetime=s.scheduled_datetime,
                    status=s.status.value,
                    price=float(s.price),
                    student_name=s.student_name,
                )
                for s in scheds
            ]

        elif user.is_student:
            profile = await self._student_repo.get_by_user_id(user_id)
            if profile:
                profile_dto = UserAdminProfileDTO(
                    learning_stage=profile.learning_stage,
                    license_category_goal=profile.license_category_goal,
                    total_lessons=profile.total_lessons,
                )
            # Buscar 5 agendamentos recentes como aluno
            scheds = await self._scheduling_repo.list_by_student(
                student_id=user_id, limit=5
            )
            recent_schedulings = [
                UserAdminSchedulingDTO(
                    id=s.id,
                    scheduled_datetime=s.scheduled_datetime,
                    status=s.status.value,
                    price=float(s.price),
                    instructor_name=s.instructor_name,
                )
                for s in scheds
            ]

        return UserAdminResponseDTO(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            phone=user.phone,
            cpf=user.cpf,
            birth_date=user.birth_date,
            biological_sex=user.biological_sex,
            created_at=user.created_at,
            updated_at=user.updated_at,
            profile=profile_dto,
            recent_schedulings=recent_schedulings,
        )
