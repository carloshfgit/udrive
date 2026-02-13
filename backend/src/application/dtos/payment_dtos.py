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

    scheduling_ids: list[UUID]
    student_id: UUID


@dataclass(frozen=True)
class ProcessRefundDTO:
    """DTO para processar reembolso."""

    payment_id: UUID
    refund_percentage: int
    reason: str | None = None


@dataclass(frozen=True)
class CreateDisputeDTO:
    """DTO para criar uma disputa."""

    scheduling_id: UUID
    reason: str
    student_id: UUID


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
class StudentPriceDTO:
    """DTO de cálculo de preço all-inclusive para o aluno."""

    instructor_amount: Decimal
    platform_fee_amount: Decimal
    stripe_fee_estimate: Decimal
    total_student_price: Decimal
    payment_method: str


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
    stripe_fee_amount: Decimal | None = None
    total_student_amount: Decimal | None = None
    client_secret: str | None = None
    transfer_group: str | None = None
    refund_amount: Decimal | None = None
    refunded_at: datetime | None = None
    created_at: datetime | None = None

    # Dados opcionais enriquecidos
    student_name: str | None = None
    instructor_name: str | None = None
    scheduling_datetime: datetime | None = None

@dataclass
class CartPaymentResponseDTO:
    """DTO de resposta para checkout de carrinho (multi-aula)."""

    payments: list[PaymentResponseDTO]
    transfer_group: str
    total_amount: Decimal
    client_secret: str

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
