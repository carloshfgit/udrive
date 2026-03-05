"""
IDisputeRepository Interface

Interface para repositório de disputas.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.dispute import Dispute
from src.domain.entities.dispute_enums import DisputeStatus


class IDisputeRepository(ABC):
    """
    Interface abstrata para repositório de disputas.

    Define operações CRUD e consultas para disputas de aulas.
    """

    @abstractmethod
    async def create(self, dispute: Dispute) -> Dispute:
        """
        Cria uma nova disputa.

        Args:
            dispute: Disputa a ser criada.

        Returns:
            Disputa criada com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, dispute_id: UUID) -> Dispute | None:
        """
        Busca disputa por ID.

        Args:
            dispute_id: ID da disputa.

        Returns:
            Disputa encontrada ou None.
        """
        ...

    @abstractmethod
    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Dispute | None:
        """
        Busca disputa pelo ID do agendamento associado.

        Args:
            scheduling_id: ID do agendamento.

        Returns:
            Disputa encontrada ou None.
        """
        ...

    @abstractmethod
    async def update(self, dispute: Dispute) -> Dispute:
        """
        Atualiza uma disputa existente.

        Args:
            dispute: Disputa com dados atualizados.

        Returns:
            Disputa atualizada.
        """
        ...

    @abstractmethod
    async def list_by_status(
        self,
        status: DisputeStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Dispute]:
        """
        Lista disputas, opcionalmente filtradas por status.

        Args:
            status: Filtro por status (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de disputas ordenadas por data de criação (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def count_by_status(
        self,
        status: DisputeStatus | None = None,
    ) -> int:
        """
        Conta disputas, opcionalmente filtradas por status.

        Args:
            status: Filtro por status (opcional).

        Returns:
            Contagem de disputas.
        """
        ...
