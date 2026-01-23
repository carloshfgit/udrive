"""
Token Repository Implementation

Implementação concreta do repositório de refresh tokens usando SQLAlchemy.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.refresh_token import RefreshToken
from src.infrastructure.db.models.refresh_token_model import RefreshTokenModel


class TokenRepositoryImpl:
    """
    Implementação do repositório de refresh tokens.

    Usa SQLAlchemy 2.0+ com sintaxe moderna select().
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Inicializa o repositório.

        Args:
            session: Sessão assíncrona do SQLAlchemy.
        """
        self._session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        """
        Cria um novo refresh token.

        Args:
            token: Entidade de token a ser criada.

        Returns:
            RefreshToken: Token criado.
        """
        model = RefreshTokenModel.from_entity(token)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """
        Busca token pelo hash.

        Args:
            token_hash: Hash do token.

        Returns:
            RefreshToken | None: Token encontrado ou None.
        """
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def revoke(self, token_id: UUID) -> bool:
        """
        Revoga um token específico.

        Args:
            token_id: UUID do token a revogar.

        Returns:
            bool: True se revogado, False se não encontrado.
        """
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.id == token_id)
            .values(is_revoked=True)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """
        Revoga todos os tokens de um usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            int: Número de tokens revogados.
        """
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def delete_expired(self) -> int:
        """
        Remove tokens expirados do banco.

        Returns:
            int: Número de tokens removidos.
        """
        stmt = delete(RefreshTokenModel).where(
            RefreshTokenModel.expires_at < datetime.utcnow()
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
