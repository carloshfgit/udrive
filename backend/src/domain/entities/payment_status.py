"""
PaymentStatus Enum

Enum para status de pagamento.
"""

from enum import Enum


class PaymentStatus(str, Enum):
    """
    Status de um pagamento.

    Attributes:
        PENDING: Aguardando confirmação do gateway.
        PROCESSING: Em processamento no Stripe.
        COMPLETED: Pagamento concluído com sucesso.
        FAILED: Falha no pagamento.
        REFUNDED: Reembolsado totalmente.
        PARTIALLY_REFUNDED: Reembolsado parcialmente.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
