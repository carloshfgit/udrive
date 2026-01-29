"""
IPaymentRepository Interface

Interface para repositório de pagamentos.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus


class IPaymentRepository(ABC):
    """
    Interface abstrata para repositório de pagamentos.

    Define operações CRUD e consultas para pagamentos.
    """

    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        """
        Cria um novo pagamento.

        Args:
            payment: Pagamento a ser criado.

        Returns:
            Pagamento criado com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        """
        Busca pagamento por ID.

        Args:
            payment_id: ID do pagamento.

        Returns:
            Pagamento encontrado ou None.
        """
        ...

    @abstractmethod
    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Payment | None:
        """
        Busca pagamento pelo ID do agendamento.

        Args:
            scheduling_id: ID do agendamento.

        Returns:
            Pagamento encontrado ou None.
        """
        ...

    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        """
        Atualiza um pagamento existente.

        Args:
            payment: Pagamento com dados atualizados.

        Returns:
            Pagamento atualizado.
        """
        ...

    @abstractmethod
    async def list_by_student(
        self,
        student_id: UUID,
        status: PaymentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Payment]:
        """
        Lista pagamentos de um aluno.

        Args:
            student_id: ID do aluno.
            status: Filtro por status (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de pagamentos ordenados por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def list_by_instructor(
        self,
        instructor_id: UUID,
        status: PaymentStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Payment]:
        """
        Lista pagamentos de um instrutor.

        Args:
            instructor_id: ID do instrutor.
            status: Filtro por status (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de pagamentos ordenados por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def count_by_student(
        self,
        student_id: UUID,
        status: PaymentStatus | None = None,
    ) -> int:
        """
        Conta pagamentos de um aluno.

        Args:
            student_id: ID do aluno.
            status: Filtro por status (opcional).

        Returns:
            Contagem de pagamentos.
        """
        ...

    @abstractmethod
    async def count_by_instructor(
        self,
        instructor_id: UUID,
        status: PaymentStatus | None = None,
    ) -> int:
        """
        Conta pagamentos de um instrutor.

        Args:
            instructor_id: ID do instrutor.
            status: Filtro por status (opcional).

        Returns:
            Contagem de pagamentos.
        """
        ...
