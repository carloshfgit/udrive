"""
Search Users Use Case

Busca usuários por nome, email ou CPF para o admin panel.
"""

from src.application.dtos.admin_user_dtos import (
    SearchUsersDTO,
    UserAdminResponseDTO,
)
from src.domain.interfaces.user_repository import IUserRepository


class SearchUsersUseCase:
    """Busca usuários por texto (nome, email, CPF)."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository

    async def execute(self, dto: SearchUsersDTO) -> list[UserAdminResponseDTO]:
        """Executa a busca de usuários."""
        users = await self._user_repo.search(
            query=dto.query,
            limit=dto.limit,
        )

        return [
            UserAdminResponseDTO(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                user_type=u.user_type.value,
                is_active=u.is_active,
                is_verified=u.is_verified,
                phone=u.phone,
                cpf=u.cpf,
                birth_date=u.birth_date,
                biological_sex=u.biological_sex,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ]
