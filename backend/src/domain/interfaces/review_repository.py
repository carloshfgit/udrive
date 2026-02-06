"""
IReviewRepository Interface

Interface para repositório de avaliações de aulas.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.review import Review


class IReviewRepository(ABC):
    """
    Interface abstrata para repositório de avaliações.
    """

    @abstractmethod
    async def create(self, review: Review) -> Review:
        """
        Salva uma nova avaliação.

        Args:
            review: Avaliação a ser criada.

        Returns:
            Avaliação salva.
        """
        ...

    @abstractmethod
    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Review | None:
        """
        Busca uma avaliação pelo ID do agendamento.

        Args:
            scheduling_id: ID do agendamento.

        Returns:
            Avaliação encontrada ou None.
        """
        ...

    @abstractmethod
    async def get_by_instructor_id(self, instructor_id: UUID) -> list[Review]:
        """
        Busca todas as avaliações de um instrutor.

        Args:
            instructor_id: ID do instrutor.

        Returns:
            Lista de avaliações.
        """
        ...
