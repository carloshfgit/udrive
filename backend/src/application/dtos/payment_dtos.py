"""
Payment DTOs

Data Transfer Objects para operações de pagamento.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# === Input DTOs ===


@dataclass(frozen=True)
class ProcessPaymentDTO:
    """DTO para processar pagamento de agendamento."""

    scheduling_id: UUID
    student_id: UUID


@dataclass(frozen=True)
class ProcessRefundDTO:
    """DTO para processar reembolso."""

    payment_id: UUID
    refund_percentage: int
    reason: str | None = None


@dataclass(frozen=True)
class GetPaymentHistoryDTO:
    """DTO para obter histórico de pagamentos."""

    user_id: UUID
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class ConnectStripeAccountDTO:
    """DTO para conectar conta Stripe do instrutor."""

    instructor_id: UUID
    email: str
    refresh_url: str
    return_url: str


# === Output DTOs ===


@dataclass
class SplitCalculationDTO:
    """DTO com cálculo do split de pagamento."""

    total_amount: Decimal
    platform_fee_percentage: Decimal
    platform_fee_amount: Decimal
    instructor_amount: Decimal


@dataclass
class PaymentResponseDTO:
    """DTO de resposta para pagamento."""

    id: UUID
    scheduling_id: UUID
    student_id: UUID
    instructor_id: UUID
    amount: Decimal
    platform_fee_amount: Decimal
    instructor_amount: Decimal
    status: str
    stripe_payment_intent_id: str | None = None
    refund_amount: Decimal | None = None
    refunded_at: datetime | None = None
    created_at: datetime | None = None

    # Dados opcionais enriquecidos
    student_name: str | None = None
    instructor_name: str | None = None
    scheduling_datetime: datetime | None = None


@dataclass
class RefundResultDTO:
    """DTO de resultado de reembolso."""

    payment_id: UUID
    refund_amount: Decimal
    refund_percentage: int
    status: str
    refunded_at: datetime


@dataclass
class PaymentHistoryResponseDTO:
    """DTO de resposta para lista paginada de pagamentos."""

    payments: list[PaymentResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool


@dataclass
class StripeConnectResponseDTO:
    """DTO de resposta para conexão Stripe Connect."""

    account_id: str
    onboarding_url: str
    is_connected: bool = False


@dataclass
class InstructorEarningsDTO:
    """DTO de ganhos do instrutor."""

    instructor_id: UUID
    total_earnings: Decimal
    pending_earnings: Decimal
    completed_lessons: int
    period_start: datetime | None = None
    period_end: datetime | None = None
