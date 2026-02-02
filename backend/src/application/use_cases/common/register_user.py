"""
Register User Use Case

Caso de uso para registro de novos usuários no sistema.
"""

from dataclasses import dataclass

from src.application.dtos.auth_dtos import RegisterUserDTO, UserResponseDTO
from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.student_profile import StudentProfile
from src.domain.entities.user import User
from src.domain.entities.user_type import UserType
from src.domain.exceptions import UserAlreadyExistsException
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.student_repository import IStudentRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class RegisterUserUseCase:
    """
    Caso de uso para cadastro de novos usuários.

    Fluxo:
        1. Verificar se email já existe
        2. Hash da senha
        3. Criar entidade User
        4. Persistir via repositório
        5. Retornar dados do usuário (sem senha)
    """

    user_repository: IUserRepository
    instructor_repository: IInstructorRepository
    student_repository: IStudentRepository
    auth_service: IAuthService

    async def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        """
        Executa o registro de um novo usuário.

        Args:
            dto: Dados do usuário a ser registrado.

        Returns:
            UserResponseDTO: Dados do usuário criado (sem senha).

        Raises:
            UserAlreadyExistsException: Se email já existir.
        """
        # Verificar se email já existe
        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user is not None:
            raise UserAlreadyExistsException(dto.email)

        # Hash da senha
        hashed_password = self.auth_service.hash_password(dto.password)

        # Criar entidade
        user = User(
            email=dto.email,
            hashed_password=hashed_password,
            full_name=dto.full_name,
            user_type=dto.user_type,
        )

        # Persistir
        created_user = await self.user_repository.create(user)

        # Criar perfil específico baseada no tipo
        if created_user.user_type == UserType.INSTRUCTOR:
            instructor_profile = InstructorProfile(user_id=created_user.id)
            await self.instructor_repository.create(instructor_profile)
        elif created_user.user_type == UserType.STUDENT:
            student_profile = StudentProfile(user_id=created_user.id)
            await self.student_repository.create(student_profile)

        # Retornar DTO de resposta (sem senha)
        return UserResponseDTO(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            user_type=created_user.user_type,
            is_active=created_user.is_active,
            is_verified=created_user.is_verified,
        )
