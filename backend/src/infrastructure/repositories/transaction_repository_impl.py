"""
Transaction Repository Implementation

Implementação do repositório de transações usando SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.transaction import Transaction
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.infrastructure.db.models.transaction_model import TransactionModel


class TransactionRepositoryImpl(ITransactionRepository):
    """Implementação do repositório de transações."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, transaction: Transaction) -> Transaction:
        model = TransactionModel.from_entity(transaction)
        self.session.add(model)
        await self.session.flush()
        return model.to_entity()

    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        model = await self.session.get(TransactionModel, transaction_id)
        return model.to_entity() if model else None

    async def list_by_user(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Transaction]:
        query = (
            select(TransactionModel)
            .where(TransactionModel.user_id == user_id)
            .order_by(TransactionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [model.to_entity() for model in result.scalars()]

    async def list_by_payment(self, payment_id: UUID) -> list[Transaction]:
        query = (
            select(TransactionModel)
            .where(TransactionModel.payment_id == payment_id)
            .order_by(TransactionModel.created_at.asc())
        )
        result = await self.session.execute(query)
        return [model.to_entity() for model in result.scalars()]
    
    async def count_by_user(self, user_id: UUID) -> int:
        query = select(func.count()).where(TransactionModel.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one() or 0
