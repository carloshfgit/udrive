"""
Push Token Repository Implementation

Implementação concreta do repositório de push tokens Expo.
Gerencia os tokens de dispositivo para envio de push notifications.
"""

from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models.push_token_model import PushTokenModel


class PushTokenRepositoryImpl:
    """
    Implementação do repositório de push tokens.

    Usa upsert manual: se o token já existe no banco, apenas o reativa;
    caso contrário, cria um novo registro. Isso evita duplicatas e mantém
    um token por dispositivo.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_or_update(
        self,
        user_id: UUID,
        token: str,
        device_id: str | None = None,
        platform: str | None = None,
    ) -> None:
        """
        Cria ou reativa um push token.

        Se o token já existe (mesmo usuário ou outro), ele é atribuído ao
        usuário atual e reativado. Caso contrário, é criado do zero.

        Args:
            user_id: UUID do usuário dono do dispositivo.
            token: Expo Push Token do dispositivo.
            device_id: Identificador opcional do dispositivo.
            platform: Plataforma ('ios' | 'android').
        """
        # Verificar se o token já existe
        stmt = select(PushTokenModel).where(PushTokenModel.token == token)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Reativar e reassociar ao usuário atual (pode ter mudado de conta)
            existing.user_id = user_id
            existing.device_id = device_id
            existing.platform = platform
            existing.is_active = True
        else:
            model = PushTokenModel(
                id=uuid4(),
                user_id=user_id,
                token=token,
                device_id=device_id,
                platform=platform,
                is_active=True,
            )
            self._session.add(model)

        await self._session.flush()

    async def get_active_tokens_by_user(self, user_id: UUID) -> list[str]:
        """
        Retorna todos os tokens de push ativos do usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Lista de strings com os tokens Expo ativos.
        """
        stmt = (
            select(PushTokenModel.token)
            .where(PushTokenModel.user_id == user_id)
            .where(PushTokenModel.is_active == True)  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def deactivate_token(self, token: str) -> None:
        """
        Desativa um push token inválido (ex: DeviceNotRegistered).

        Args:
            token: Expo Push Token a ser desativado.
        """
        stmt = (
            update(PushTokenModel)
            .where(PushTokenModel.token == token)
            .values(is_active=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_token(self, token: str, user_id: UUID) -> bool:
        """
        Remove completamente um push token (logout ou desinstalação).

        Só remove se pertencer ao usuário informado (evita acesso não autorizado).

        Args:
            token: Expo Push Token a remover.
            user_id: UUID do proprietário do token.

        Returns:
            True se removido, False se não encontrado.
        """
        stmt = (
            delete(PushTokenModel)
            .where(PushTokenModel.token == token)
            .where(PushTokenModel.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0
