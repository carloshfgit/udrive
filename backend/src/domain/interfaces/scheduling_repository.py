"""
ISchedulingRepository Interface

Interface para repositório de agendamentos.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence
from uuid import UUID

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


class ISchedulingRepository(ABC):
    """
    Interface abstrata para repositório de agendamentos.

    Define operações CRUD e consultas para agendamentos de aulas.
    """

    @abstractmethod
    async def create(self, scheduling: Scheduling) -> Scheduling:
        """
        Cria um novo agendamento.

        Args:
            scheduling: Agendamento a ser criado.

        Returns:
            Agendamento criado com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        """
        Busca agendamento por ID.

        Args:
            scheduling_id: ID do agendamento.

        Returns:
            Agendamento encontrado ou None.
        """
        ...

    @abstractmethod
    async def update(self, scheduling: Scheduling) -> Scheduling:
        """
        Atualiza um agendamento existente.

        Args:
            scheduling: Agendamento com dados atualizados.

        Returns:
            Agendamento atualizado.
        """
        ...

    @abstractmethod
    async def delete(self, scheduling_id: UUID) -> bool:
        """
        Remove um agendamento.

        Args:
            scheduling_id: ID do agendamento a remover.

        Returns:
            True se removido, False se não encontrado.
        """
        ...

    @abstractmethod
    async def list_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Scheduling]:
        """
        Lista agendamentos de um aluno.

        Args:
            student_id: ID do aluno.
            status: Filtro por status (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de agendamentos ordenados por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def list_by_instructor(
        self,
        instructor_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Scheduling]:
        """
        Lista agendamentos de um instrutor.

        Args:
            instructor_id: ID do instrutor.
            status: Filtro por status (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de agendamentos ordenados por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def get_next_instructor_scheduling(
        self,
        instructor_id: UUID,
    ) -> Scheduling | None:
        """
        Busca a próxima aula (pendente, confirmada ou reagendamento) do instrutor.

        Args:
            instructor_id: ID do instrutor.

        Returns:
            A aula mais próxima no futuro ou None.
        """
        ...

    @abstractmethod
    async def get_next_student_scheduling(
        self,
        student_id: UUID,
    ) -> Scheduling | None:
        """
        Busca a próxima aula (pendente, confirmada ou reagendamento) do aluno.

        Args:
            student_id: ID do aluno.

        Returns:
            A aula mais próxima no futuro ou None.
        """
        ...

    @abstractmethod
    async def check_conflict(
        self,
        instructor_id: UUID,
        scheduled_datetime: datetime,
        duration_minutes: int,
        exclude_scheduling_id: UUID | None = None,
    ) -> bool:
        """
        Verifica se há conflito de horário para o instrutor.

        Args:
            instructor_id: ID do instrutor.
            scheduled_datetime: Data/hora do agendamento.
            duration_minutes: Duração em minutos.
            exclude_scheduling_id: ID de agendamento a excluir da verificação.

        Returns:
            True se há conflito, False caso contrário.
        """
        ...

    @abstractmethod
    async def count_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | None = None,
    ) -> int:
        """
        Conta agendamentos de um aluno.

        Args:
            student_id: ID do aluno.
            status: Filtro por status (opcional).

        Returns:
            Contagem de agendamentos.
        """
        ...

    @abstractmethod
    async def count_by_instructor(
        self,
        instructor_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
    ) -> int:
        """
        Conta agendamentos de um instrutor.

        Args:
            instructor_id: ID do instrutor.
            status: Filtro por status (opcional).

        Returns:
            Contagem de agendamentos.
        """
        ...

    @abstractmethod
    async def list_by_student_and_instructor(
        self,
        student_id: UUID,
        instructor_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Scheduling]:
        """
        Lista agendamentos entre um aluno e um instrutor específico.

        Args:
            student_id: ID do aluno.
            instructor_id: ID do instrutor.
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de agendamentos ordenados por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def list_by_instructor_and_date(
        self,
        instructor_id: UUID,
        date: "date",
    ) -> list[Scheduling]:
        """
        Lista agendamentos de um instrutor para uma data específica.

        Args:
            instructor_id: ID do instrutor.
            date: Data para filtrar agendamentos.

        Returns:
            Lista de agendamentos do dia ordenados por hora.
        """
        ...

    @abstractmethod
    async def get_scheduling_dates_for_month(
        self,
        instructor_id: UUID,
        year: int,
        month: int,
    ) -> list["date"]:
        """
        Retorna lista de datas únicas com agendamentos no mês.

        Args:
            instructor_id: ID do instrutor.
            year: Ano.
            month: Mês (1-12).

        Returns:
            Lista de datas que possuem agendamentos (não cancelados).
        """
        ...

