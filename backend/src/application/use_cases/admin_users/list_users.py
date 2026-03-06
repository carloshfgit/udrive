"""
List Users Use Case

Lista todos os usuários com filtros e paginação para o admin panel.
"""

from src.application.dtos.admin_user_dtos import (
    ListUsersDTO,
    UserAdminResponseDTO,
    UserListResponseDTO,
)
from src.domain.interfaces.user_repository import IUserRepository


class ListUsersUseCase:
    """Lista usuários com filtros para o painel administrativo."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository

    async def execute(self, dto: ListUsersDTO) -> UserListResponseDTO:
        """Executa a listagem de usuários."""
        users = await self._user_repo.list_all(
            user_type=dto.user_type,
            is_active=dto.is_active,
            limit=dto.limit,
            offset=dto.offset,
        )

        total_count = await self._user_repo.count_all(
            user_type=dto.user_type,
            is_active=dto.is_active,
        )

        user_dtos = [
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

        return UserListResponseDTO(
            users=user_dtos,
            total_count=total_count,
            limit=dto.limit,
            offset=dto.offset,
            has_more=(dto.offset + dto.limit) < total_count,
        )
