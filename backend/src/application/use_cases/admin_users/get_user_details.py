"""
Get User Details Use Case

Obtém detalhes completos de um usuário para o admin panel.
"""

from uuid import UUID

from src.application.dtos.admin_user_dtos import UserAdminResponseDTO
from src.domain.interfaces.user_repository import IUserRepository


class GetUserDetailsUseCase:
    """Obtém detalhes de um usuário para o painel administrativo."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository

    async def execute(self, user_id: UUID) -> UserAdminResponseDTO | None:
        """Busca detalhes completos de um usuário."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            return None

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
        )
