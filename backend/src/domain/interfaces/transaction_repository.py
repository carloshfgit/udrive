"""
ITransactionRepository Interface

Interface para repositório de transações financeiras.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.transaction import Transaction
from src.domain.entities.transaction_type import TransactionType


class ITransactionRepository(ABC):
    """
    Interface abstrata para repositório de transações.

    Define operações CRUD e consultas para transações financeiras.
    """

    @abstractmethod
    async def create(self, transaction: Transaction) -> Transaction:
        """
        Cria uma nova transação.

        Args:
            transaction: Transação a ser criada.

        Returns:
            Transação criada com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Transaction | None:
        """
        Busca transação por ID.

        Args:
            transaction_id: ID da transação.

        Returns:
            Transação encontrada ou None.
        """
        ...

    @abstractmethod
    async def list_by_payment(self, payment_id: UUID) -> list[Transaction]:
        """
        Lista transações de um pagamento.

        Args:
            payment_id: ID do pagamento.

        Returns:
            Lista de transações ordenadas por data.
        """
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        transaction_type: TransactionType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        """
        Lista transações de um usuário.

        Args:
            user_id: ID do usuário.
            transaction_type: Filtro por tipo (opcional).
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de transações ordenadas por data (mais recentes primeiro).
        """
        ...

    @abstractmethod
    async def count_by_user(
        self,
        user_id: UUID,
        transaction_type: TransactionType | None = None,
    ) -> int:
        """
        Conta transações de um usuário.

        Args:
            user_id: ID do usuário.
            transaction_type: Filtro por tipo (opcional).

        Returns:
            Contagem de transações.
        """
        ...
