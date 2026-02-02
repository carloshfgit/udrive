"""
StudentRepository Implementation

Implementação concreta do repositório de alunos.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.student_profile import StudentProfile
from src.domain.interfaces.student_repository import IStudentRepository
from src.infrastructure.db.models.student_profile_model import StudentProfileModel


class StudentRepositoryImpl(IStudentRepository):
    """
    Implementação do repositório de alunos usando SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, profile: StudentProfile) -> StudentProfile:
        """Cria um novo perfil de aluno."""
        model = StudentProfileModel.from_entity(profile)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, profile_id: UUID) -> StudentProfile | None:
        """Busca perfil por ID."""
        stmt = select(StudentProfileModel).where(
            StudentProfileModel.id == profile_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_user_id(self, user_id: UUID) -> StudentProfile | None:
        """Busca perfil pelo ID do usuário."""
        stmt = select(StudentProfileModel).where(
            StudentProfileModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, profile: StudentProfile) -> StudentProfile:
        """Atualiza um perfil existente."""
        stmt = select(StudentProfileModel).where(
            StudentProfileModel.id == profile.id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Perfil não encontrado: {profile.id}")

        # Atualizar campos
        model.preferred_schedule = profile.preferred_schedule
        model.license_category_goal = profile.license_category_goal
        model.learning_stage = profile.learning_stage
        model.notes = profile.notes
        model.total_lessons = profile.total_lessons
        model.total_lessons = profile.total_lessons

        await self._session.commit()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, profile_id: UUID) -> bool:
        """Remove um perfil."""
        stmt = select(StudentProfileModel).where(
            StudentProfileModel.id == profile_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.commit()
        return True
