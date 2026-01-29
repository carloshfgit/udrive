"""
IAvailabilityRepository Interface

Interface para repositório de disponibilidade de instrutores.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.availability import Availability


class IAvailabilityRepository(ABC):
    """
    Interface abstrata para repositório de disponibilidade.

    Define operações CRUD e consultas para slots de disponibilidade.
    """

    @abstractmethod
    async def create(self, availability: Availability) -> Availability:
        """
        Cria um novo slot de disponibilidade.

        Args:
            availability: Slot a ser criado.

        Returns:
            Slot criado com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, availability_id: UUID) -> Availability | None:
        """
        Busca slot por ID.

        Args:
            availability_id: ID do slot.

        Returns:
            Slot encontrado ou None.
        """
        ...

    @abstractmethod
    async def update(self, availability: Availability) -> Availability:
        """
        Atualiza um slot existente.

        Args:
            availability: Slot com dados atualizados.

        Returns:
            Slot atualizado.
        """
        ...

    @abstractmethod
    async def delete(self, availability_id: UUID) -> bool:
        """
        Remove um slot de disponibilidade.

        Args:
            availability_id: ID do slot a remover.

        Returns:
            True se removido, False se não encontrado.
        """
        ...

    @abstractmethod
    async def list_by_instructor(
        self,
        instructor_id: UUID,
        only_active: bool = True,
    ) -> list[Availability]:
        """
        Lista todos os slots de um instrutor.

        Args:
            instructor_id: ID do instrutor.
            only_active: Se True, retorna apenas slots ativos.

        Returns:
            Lista de slots ordenados por dia da semana e hora de início.
        """
        ...

    @abstractmethod
    async def get_by_instructor_and_day(
        self,
        instructor_id: UUID,
        day_of_week: int,
        only_active: bool = True,
    ) -> list[Availability]:
        """
        Lista slots de um instrutor para um dia específico.

        Args:
            instructor_id: ID do instrutor.
            day_of_week: Dia da semana (0-6).
            only_active: Se True, retorna apenas slots ativos.

        Returns:
            Lista de slots para o dia especificado.
        """
        ...

    @abstractmethod
    async def is_time_available(
        self,
        instructor_id: UUID,
        target_datetime: datetime,
        duration_minutes: int,
    ) -> bool:
        """
        Verifica se um horário está dentro da disponibilidade do instrutor.

        Considera apenas os slots ativos configurados pelo instrutor.

        Args:
            instructor_id: ID do instrutor.
            target_datetime: Data/hora alvo.
            duration_minutes: Duração necessária em minutos.

        Returns:
            True se o horário está disponível na configuração do instrutor.
        """
        ...

    @abstractmethod
    async def check_overlap(
        self,
        instructor_id: UUID,
        day_of_week: int,
        start_time: "time",
        end_time: "time",
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Verifica se há sobreposição com slots existentes.

        Args:
            instructor_id: ID do instrutor.
            day_of_week: Dia da semana.
            start_time: Hora de início.
            end_time: Hora de término.
            exclude_id: ID de slot a excluir da verificação.

        Returns:
            True se há sobreposição.
        """
        ...
