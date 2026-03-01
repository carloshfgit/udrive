"""
Notification Repository Implementation

Implementação concreta do INotificationRepository usando SQLAlchemy async.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.notification import Notification
from src.infrastructure.db.models.notification_model import NotificationModel


class NotificationRepositoryImpl:
    """
    Implementação concreta do repositório de notificações.

    Usa SQLAlchemy 2.0+ com sintaxe moderna select().
    Usa flush() em vez de commit() para ser compatível com sessões
    gerenciadas pelo FastAPI (a sessão é fechada automaticamente ao fim
    do request dentro do contexto de get_db()).
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        """
        Persiste uma nova notificação.

        Args:
            notification: Entidade de domínio a ser criada.

        Returns:
            Notification: Notificação persistida.
        """
        model = NotificationModel.from_entity(notification)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """
        Retorna notificações do usuário, mais recentes primeiro.

        Args:
            user_id: UUID do usuário.
            limit: Quantidade máxima a retornar (para paginação).
            offset: Posição de início (para paginação).

        Returns:
            Lista de Notification ordenada por created_at desc.
        """
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [m.to_entity() for m in result.scalars().all()]

    async def count_unread(self, user_id: UUID) -> int:
        """
        Conta notificações não lidas do usuário.

        Args:
            user_id: UUID do usuário.

        Returns:
            Quantidade de notificações não lidas.
        """
        stmt = (
            select(func.count())
            .select_from(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def mark_as_read(
        self, notification_id: UUID, user_id: UUID
    ) -> bool:
        """
        Marca uma notificação como lida.

        Args:
            notification_id: UUID da notificação.
            user_id: UUID do proprietário (evita acesso não autorizado).

        Returns:
            True se a notificação foi atualizada, False se não encontrada.
        """
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)  # noqa: E712
            .values(
                is_read=True,
                read_at=datetime.now(tz=timezone.utc),
            )
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas as notificações não lidas do usuário como lidas.

        Args:
            user_id: UUID do usuário.

        Returns:
            Quantidade de notificações atualizadas.
        """
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)  # noqa: E712
            .values(
                is_read=True,
                read_at=datetime.now(tz=timezone.utc),
            )
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
