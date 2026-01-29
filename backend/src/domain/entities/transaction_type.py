"""
TransactionType Enum

Enum para tipos de transação financeira.
"""

from enum import Enum


class TransactionType(str, Enum):
    """
    Tipo de transação financeira.

    Attributes:
        PAYMENT: Pagamento de aula.
        REFUND: Reembolso ao aluno.
        PLATFORM_FEE: Taxa da plataforma.
        INSTRUCTOR_PAYOUT: Repasse ao instrutor.
    """

    PAYMENT = "payment"
    REFUND = "refund"
    PLATFORM_FEE = "platform_fee"
    INSTRUCTOR_PAYOUT = "instructor_payout"
