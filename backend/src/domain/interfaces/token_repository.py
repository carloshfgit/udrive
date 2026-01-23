"""
Token Repository Interface

Define o contrato para operações de persistência de tokens.
"""

from typing import Protocol
from uuid import UUID

from src.domain.entities.refresh_token import RefreshToken


class ITokenRepository(Protocol):
    """
    Interface para repositório de refresh tokens.

    Implementações concretas devem fornecer persistência e revogação.
    """

    async def create(self, token: RefreshToken) -> RefreshToken:
        """
        Cria um novo refresh token.

        Args:
            token: Entidade de token a ser criada.

        Returns:
            RefreshToken: Token criado com ID populado.
        """
        ...

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Busca token pelo hash.

        Args:
            token_hash: Hash do token.

        Returns:
            RefreshToken | None: Token encontrado ou None.
        """
        ...

    async def revoke(self, token_id: UUID) -> bool:
        """
        Revoga um token específico.

        Args:
            token_id: UUID do token a revogar.

        Returns:
            bool: True se revogado, False se não encontrado.
        """
        ...

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """
        Revoga todos os tokens de um usuário.

        Usado para logout de todas as sessões.

        Args:
            user_id: UUID do usuário.

        Returns:
            int: Número de tokens revogados.
        """
        ...

    async def delete_expired(self) -> int:
        """
        Remove tokens expirados do banco.

        Returns:
            int: Número de tokens removidos.
        """
        ...
