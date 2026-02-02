"""
Update Student Profile Use Case

Caso de uso para criar ou atualizar perfil de aluno.
"""

from dataclasses import dataclass

from src.application.dtos.profile_dtos import (
    StudentProfileResponseDTO,
    UpdateStudentProfileDTO,
)
from src.domain.entities.student_profile import StudentProfile
from src.domain.entities.user_type import UserType
from src.domain.exceptions import StudentNotFoundException, UserNotFoundException
from src.domain.interfaces.student_repository import IStudentRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class UpdateStudentProfileUseCase:
    """
    Caso de uso para criar ou atualizar perfil de aluno.

    Fluxo:
        1. Verificar se usuário existe e é aluno
        2. Buscar perfil existente ou criar novo
        3. Atualizar campos fornecidos
        4. Persistir alterações
        5. Retornar perfil atualizado
    """

    user_repository: IUserRepository
    student_repository: IStudentRepository

    async def execute(self, dto: UpdateStudentProfileDTO) -> StudentProfileResponseDTO:
        """
        Executa a criação ou atualização do perfil.

        Args:
            dto: Dados do perfil a atualizar.

        Returns:
            StudentProfileResponseDTO: Perfil atualizado.

        Raises:
            UserNotFoundException: Se usuário não existir.
            StudentNotFoundException: Se usuário não for aluno.
        """
        # Verificar se usuário existe
        user = await self.user_repository.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundException(str(dto.user_id))

        # Verificar se é aluno
        if user.user_type != UserType.STUDENT:
            raise StudentNotFoundException(
                f"Usuário {dto.user_id} não é um aluno"
            )

        # Buscar perfil existente ou criar novo
        profile = await self.student_repository.get_by_user_id(dto.user_id)

        if profile is None:
            # Criar novo perfil
            profile = StudentProfile(user_id=dto.user_id)

        # Atualizar campos fornecidos
        profile.update_profile(
            preferred_schedule=dto.preferred_schedule,
            license_category_goal=dto.license_category_goal,
            learning_stage=dto.learning_stage,
            notes=dto.notes,

        )

        # Atualizar dados do usuário
        if dto.phone is not None:
            user.phone = dto.phone
        if dto.cpf is not None:
            user.cpf = dto.cpf
        if dto.birth_date is not None:
            user.birth_date = dto.birth_date
        
        # Persistir usuário
        await self.user_repository.update(user)

        # Persistir (criar ou atualizar)
        if await self.student_repository.get_by_user_id(dto.user_id) is None:
            saved_profile = await self.student_repository.create(profile)
        else:
            saved_profile = await self.student_repository.update(profile)

        return StudentProfileResponseDTO(
            id=saved_profile.id,
            user_id=saved_profile.user_id,
            preferred_schedule=saved_profile.preferred_schedule,
            license_category_goal=saved_profile.license_category_goal,
            learning_stage=saved_profile.learning_stage,
            notes=saved_profile.notes,
            total_lessons=saved_profile.total_lessons,
            phone=user.phone or "",
            cpf=user.cpf or "",
            birth_date=user.birth_date,
        )
