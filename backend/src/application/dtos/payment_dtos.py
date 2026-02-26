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
class CreateCheckoutDTO:
    """DTO para criar checkout do Mercado Pago (multi-item)."""

    scheduling_ids: list[UUID]
    student_id: UUID
    student_email: str | None = None
    return_url: str | None = None


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
class ConnectGatewayAccountDTO:
    """DTO para conectar conta de pagamento do instrutor."""

    instructor_id: UUID
    email: str
    refresh_url: str
    return_url: str


@dataclass(frozen=True)
class OAuthCallbackDTO:
    """DTO para processar callback OAuth do Mercado Pago."""

    code: str
    state: str  # instructor user_id (encrypted)


@dataclass
class OAuthAuthorizeResponseDTO:
    """DTO de resposta com URL de autorização OAuth."""

    authorization_url: str
    state: str


@dataclass
class OAuthCallbackResponseDTO:
    """DTO de resposta após callback OAuth."""

    mp_user_id: str
    is_connected: bool
    return_url: str | None = None


# === Webhook DTOs ===


@dataclass(frozen=True)
class WebhookNotificationDTO:
    """DTO para notificação recebida do webhook Mercado Pago."""

    notification_id: int
    notification_type: str  # "payment"
    action: str  # "payment.updated"
    data_id: str  # ID do pagamento no MP
    live_mode: bool = True
    user_id: str | None = None  # MP user ID of the application that received the notification


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
    gateway_payment_id: str | None = None
    refund_amount: Decimal | None = None
    refunded_at: datetime | None = None
    created_at: datetime | None = None

    # Dados opcionais enriquecidos
    student_name: str | None = None
    instructor_name: str | None = None
    scheduling_datetime: datetime | None = None


@dataclass
class CheckoutResponseDTO:
    """DTO de resposta do checkout com URL de pagamento."""

    payment_id: UUID
    preference_id: str
    checkout_url: str
    sandbox_url: str | None = None
    status: str = "processing"


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
class GatewayConnectResponseDTO:
    """DTO de resposta para conexão de conta de pagamento."""

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


@dataclass(frozen=True)
class CancelSchedulingDTO:
    """DTO para cancelar agendamento com reembolso automático."""

    scheduling_id: UUID
    cancelled_by: UUID  # ID do usuário que está cancelando
    reason: str | None = None


@dataclass
class CancelSchedulingResultDTO:
    """DTO de resultado do cancelamento com reembolso."""

    scheduling_id: UUID
    status: str  # "cancelled"
    refund_percentage: int
    refund_amount: Decimal | None = None
    refund_status: str | None = None  # "approved" / None se 0%

