"""
Logout User Use Case

Caso de uso para logout (revogação de tokens).
"""

from dataclasses import dataclass
from uuid import UUID

from src.domain.interfaces.token_repository import ITokenRepository


@dataclass
class LogoutUserUseCase:
    """
    Caso de uso para logout de usuários.

    Revoga o refresh token atual ou todos os tokens do usuário.
    """

    token_repository: ITokenRepository

    async def execute(self, token_id: UUID, revoke_all: bool = False, user_id: UUID | None = None) -> int:
        """
        Executa o logout.

        Args:
            token_id: ID do token a revogar.
            revoke_all: Se True, revoga todos os tokens do usuário.
            user_id: ID do usuário (obrigatório se revoke_all=True).

        Returns:
            int: Número de tokens revogados.
        """
        if revoke_all and user_id is not None:
            # Revogar todos os tokens do usuário
            return await self.token_repository.revoke_all_for_user(user_id)

        # Revogar apenas o token atual
        success = await self.token_repository.revoke(token_id)
        return 1 if success else 0
