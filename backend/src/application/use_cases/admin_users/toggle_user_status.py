"""
Toggle User Status Use Case

Ativa ou desativa um usuário (toggle is_active).
"""

from datetime import datetime

import structlog

from src.application.dtos.admin_user_dtos import (
    ToggleUserStatusDTO,
    UserAdminResponseDTO,
)
from src.domain.interfaces.user_repository import IUserRepository

logger = structlog.get_logger()


class UserNotFoundException(Exception):
    """Exceção quando usuário não é encontrado."""

    pass


class ToggleUserStatusUseCase:
    """Ativa ou desativa um usuário."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repo = user_repository

    async def execute(self, dto: ToggleUserStatusDTO) -> UserAdminResponseDTO:
        """Inverte o status is_active do usuário."""
        user = await self._user_repo.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundException(f"Usuário não encontrado: {dto.user_id}")

        # Toggle is_active
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()

        updated = await self._user_repo.update(user)

        logger.info(
            "admin_toggle_user_status",
            user_id=str(dto.user_id),
            admin_id=str(dto.admin_id),
            new_status="active" if updated.is_active else "inactive",
        )

        return UserAdminResponseDTO(
            id=updated.id,
            email=updated.email,
            full_name=updated.full_name,
            user_type=updated.user_type.value,
            is_active=updated.is_active,
            is_verified=updated.is_verified,
            phone=updated.phone,
            cpf=updated.cpf,
            birth_date=updated.birth_date,
            biological_sex=updated.biological_sex,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
