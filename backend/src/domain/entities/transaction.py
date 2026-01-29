"""
Transaction Entity

Entidade de domínio representando uma transação financeira.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from .transaction_type import TransactionType


@dataclass
class Transaction:
    """
    Entidade de transação financeira.

    Registra movimentações financeiras associadas a pagamentos.

    Attributes:
        payment_id: ID do pagamento (FK para Payment).
        user_id: ID do usuário relacionado (FK para User).
        type: Tipo da transação.
        amount: Valor da transação em BRL.
        description: Descrição da transação.
        stripe_reference_id: ID de referência no Stripe.
    """

    payment_id: UUID
    user_id: UUID
    type: TransactionType
    amount: Decimal
    description: str
    stripe_reference_id: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if self.amount < 0:
            raise ValueError("Valor da transação não pode ser negativo")
        if not self.description:
            raise ValueError("Descrição da transação é obrigatória")

    @property
    def is_credit(self) -> bool:
        """Verifica se é uma transação de crédito para o usuário."""
        return self.type in (
            TransactionType.INSTRUCTOR_PAYOUT,
            TransactionType.REFUND,
        )

    @property
    def is_debit(self) -> bool:
        """Verifica se é uma transação de débito do usuário."""
        return self.type == TransactionType.PAYMENT

    @classmethod
    def create_payment_transaction(
        cls,
        payment_id: UUID,
        student_id: UUID,
        amount: Decimal,
        stripe_reference_id: str | None = None,
    ) -> "Transaction":
        """
        Factory method para criar transação de pagamento.

        Args:
            payment_id: ID do pagamento.
            student_id: ID do aluno.
            amount: Valor do pagamento.
            stripe_reference_id: ID de referência no Stripe.

        Returns:
            Transaction de tipo PAYMENT.
        """
        return cls(
            payment_id=payment_id,
            user_id=student_id,
            type=TransactionType.PAYMENT,
            amount=amount,
            description="Pagamento de aula",
            stripe_reference_id=stripe_reference_id,
        )

    @classmethod
    def create_refund_transaction(
        cls,
        payment_id: UUID,
        student_id: UUID,
        amount: Decimal,
        stripe_reference_id: str | None = None,
    ) -> "Transaction":
        """
        Factory method para criar transação de reembolso.

        Args:
            payment_id: ID do pagamento.
            student_id: ID do aluno.
            amount: Valor do reembolso.
            stripe_reference_id: ID de referência no Stripe.

        Returns:
            Transaction de tipo REFUND.
        """
        return cls(
            payment_id=payment_id,
            user_id=student_id,
            type=TransactionType.REFUND,
            amount=amount,
            description="Reembolso de aula",
            stripe_reference_id=stripe_reference_id,
        )

    @classmethod
    def create_instructor_payout_transaction(
        cls,
        payment_id: UUID,
        instructor_id: UUID,
        amount: Decimal,
        stripe_reference_id: str | None = None,
    ) -> "Transaction":
        """
        Factory method para criar transação de repasse ao instrutor.

        Args:
            payment_id: ID do pagamento.
            instructor_id: ID do instrutor.
            amount: Valor do repasse.
            stripe_reference_id: ID de referência no Stripe.

        Returns:
            Transaction de tipo INSTRUCTOR_PAYOUT.
        """
        return cls(
            payment_id=payment_id,
            user_id=instructor_id,
            type=TransactionType.INSTRUCTOR_PAYOUT,
            amount=amount,
            description="Repasse de aula",
            stripe_reference_id=stripe_reference_id,
        )
