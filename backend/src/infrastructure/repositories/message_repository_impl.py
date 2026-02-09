"""
Message Repository Implementation

Implementação concreta do repositório de mensagens usando SQLAlchemy.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.message import Message
from src.domain.interfaces.message_repository import IMessageRepository
from src.infrastructure.db.models.message_model import MessageModel


class MessageRepositoryImpl(IMessageRepository):
    """Implementação do repositório de mensagens usando SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, message: Message) -> Message:
        model = MessageModel.from_entity(message)
        self._session.add(model)
        await self._session.flush()
        return model.to_entity()

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = select(MessageModel).where(MessageModel.id == message_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def list_by_conversation(
        self,
        user_a: UUID,
        user_b: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(
                or_(
                    and_(MessageModel.sender_id == user_a, MessageModel.receiver_id == user_b),
                    and_(MessageModel.sender_id == user_b, MessageModel.receiver_id == user_a),
                )
            )
            .order_by(MessageModel.timestamp.asc()) # Ordenação de chat geralmente é ASC
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]

    async def mark_as_read(self, message_ids: list[UUID]) -> None:
        if not message_ids:
            return
        
        stmt = (
            update(MessageModel)
            .where(MessageModel.id.in_(message_ids))
            .values(is_read=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_last_message_between(self, user_a: UUID, user_b: UUID) -> Message | None:
        stmt = (
            select(MessageModel)
            .where(
                or_(
                    and_(MessageModel.sender_id == user_a, MessageModel.receiver_id == user_b),
                    and_(MessageModel.sender_id == user_b, MessageModel.receiver_id == user_a),
                )
            )
            .order_by(MessageModel.timestamp.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None
