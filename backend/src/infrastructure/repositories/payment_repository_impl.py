"""
Payment Repository Implementation

Implementação do repositório de pagamentos usando SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.payment import Payment
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.infrastructure.db.models.payment_model import PaymentModel


class PaymentRepositoryImpl(IPaymentRepository):
    """Implementação do repositório de pagamentos."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, payment: Payment) -> Payment:
        model = PaymentModel.from_entity(payment)
        self.session.add(model)
        await self.session.flush()
        return model.to_entity()

    async def update(self, payment: Payment) -> Payment:
        # Busca o model existente para garantir attach na sessão
        model = await self.session.get(PaymentModel, payment.id)
        if model:
            # Atualiza campos
            model.status = payment.status
            model.stripe_payment_intent_id = payment.stripe_payment_intent_id
            model.stripe_transfer_id = payment.stripe_transfer_id
            model.refund_amount = payment.refund_amount
            model.refunded_at = payment.refunded_at
            model.updated_at = payment.updated_at
            await self.session.flush()
            return model.to_entity()
        return payment

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        model = await self.session.get(PaymentModel, payment_id)
        return model.to_entity() if model else None

    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Payment | None:
        query = select(PaymentModel).where(PaymentModel.scheduling_id == scheduling_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def list_by_student(
        self, student_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Payment]:
        query = (
            select(PaymentModel)
            .where(PaymentModel.student_id == student_id)
            .order_by(PaymentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [model.to_entity() for model in result.scalars()]

    async def list_by_instructor(
        self, instructor_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Payment]:
        query = (
            select(PaymentModel)
            .where(PaymentModel.instructor_id == instructor_id)
            .order_by(PaymentModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return [model.to_entity() for model in result.scalars()]

    async def count_by_student(self, student_id: UUID) -> int:
        query = select(func.count()).where(PaymentModel.student_id == student_id)
        result = await self.session.execute(query)
        return result.scalar_one() or 0

    async def count_by_instructor(self, instructor_id: UUID) -> int:
        query = select(func.count()).where(PaymentModel.instructor_id == instructor_id)
        result = await self.session.execute(query)
        return result.scalar_one() or 0
