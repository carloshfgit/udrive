"""
ReviewRepository Implementation

Implementação concreta do repositório de avaliações usando SQLAlchemy.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.review import Review
from src.domain.interfaces.review_repository import IReviewRepository
from src.infrastructure.db.models.review_model import ReviewModel


class ReviewRepositoryImpl(IReviewRepository):
    """
    Implementação do repositório de avaliações usando SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, review: Review) -> Review:
        """Salva uma nova avaliação."""
        model = ReviewModel.from_entity(review)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Review | None:
        """Busca avaliação pelo ID do agendamento."""
        stmt = select(ReviewModel).where(ReviewModel.scheduling_id == scheduling_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_instructor_id(self, instructor_id: UUID) -> list[Review]:
        """Busca todas as avaliações de um instrutor."""
        stmt = select(ReviewModel).where(ReviewModel.instructor_id == instructor_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [model.to_entity() for model in models]
