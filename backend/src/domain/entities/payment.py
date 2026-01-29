"""
Payment Entity

Entidade de domínio representando um pagamento de aula.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from .payment_status import PaymentStatus


@dataclass
class Payment:
    """
    Entidade de pagamento de aula.

    Representa o pagamento de um agendamento, incluindo o split entre
    instrutor e plataforma.

    Attributes:
        scheduling_id: ID do agendamento (FK para Scheduling).
        student_id: ID do aluno (FK para User).
        instructor_id: ID do instrutor (FK para User).
        amount: Valor total em BRL.
        platform_fee_percentage: Percentual da taxa da plataforma.
        platform_fee_amount: Valor da taxa da plataforma.
        instructor_amount: Valor líquido do instrutor.
        status: Status do pagamento.
        stripe_payment_intent_id: ID do PaymentIntent no Stripe.
        stripe_transfer_id: ID do Transfer no Stripe.
        refund_amount: Valor reembolsado (se aplicável).
        refunded_at: Data/hora do reembolso (se aplicável).
    """

    scheduling_id: UUID
    student_id: UUID
    instructor_id: UUID
    amount: Decimal
    platform_fee_percentage: Decimal = Decimal("15.00")  # 15% padrão
    platform_fee_amount: Decimal = Decimal("0.00")
    instructor_amount: Decimal = Decimal("0.00")
    status: PaymentStatus = PaymentStatus.PENDING
    stripe_payment_intent_id: str | None = None
    stripe_transfer_id: str | None = None
    refund_amount: Decimal | None = None
    refunded_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida campos e calcula valores após inicialização."""
        if self.amount < 0:
            raise ValueError("Valor do pagamento não pode ser negativo")
        if self.platform_fee_percentage < 0 or self.platform_fee_percentage > 100:
            raise ValueError("Taxa da plataforma deve estar entre 0 e 100")

        # Calcular valores se não fornecidos
        if self.platform_fee_amount == Decimal("0.00") and self.amount > 0:
            self.calculate_split()

    def calculate_split(self) -> None:
        """
        Calcula o split do pagamento entre plataforma e instrutor.

        A taxa da plataforma é aplicada sobre o valor total e o restante
        vai para o instrutor.
        """
        self.platform_fee_amount = (
            self.amount * self.platform_fee_percentage / Decimal("100")
        ).quantize(Decimal("0.01"))
        self.instructor_amount = self.amount - self.platform_fee_amount

    def can_refund(self) -> bool:
        """
        Verifica se o pagamento pode ser reembolsado.

        Returns:
            True se pode ser reembolsado.
        """
        return self.status == PaymentStatus.COMPLETED

    def process_refund(self, refund_percentage: int) -> Decimal:
        """
        Processa o reembolso do pagamento.

        Args:
            refund_percentage: Percentual de reembolso (0-100).

        Returns:
            Valor reembolsado.

        Raises:
            ValueError: Se não pode ser reembolsado ou percentual inválido.
        """
        if not self.can_refund():
            raise ValueError(
                f"Pagamento não pode ser reembolsado. Status atual: {self.status}"
            )

        if refund_percentage < 0 or refund_percentage > 100:
            raise ValueError("Percentual de reembolso deve estar entre 0 e 100")

        self.refund_amount = (
            self.amount * Decimal(refund_percentage) / Decimal("100")
        ).quantize(Decimal("0.01"))

        if refund_percentage == 100:
            self.status = PaymentStatus.REFUNDED
        else:
            self.status = PaymentStatus.PARTIALLY_REFUNDED

        self.refunded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        return self.refund_amount

    def mark_processing(self, stripe_payment_intent_id: str) -> None:
        """
        Marca o pagamento como em processamento.

        Args:
            stripe_payment_intent_id: ID do PaymentIntent no Stripe.
        """
        if self.status != PaymentStatus.PENDING:
            raise ValueError(
                f"Pagamento não pode ser processado. Status atual: {self.status}"
            )

        self.stripe_payment_intent_id = stripe_payment_intent_id
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, stripe_transfer_id: str | None = None) -> None:
        """
        Marca o pagamento como concluído.

        Args:
            stripe_transfer_id: ID do Transfer no Stripe.
        """
        if self.status != PaymentStatus.PROCESSING:
            raise ValueError(
                f"Pagamento não pode ser concluído. Status atual: {self.status}"
            )

        self.stripe_transfer_id = stripe_transfer_id
        self.status = PaymentStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_failed(self) -> None:
        """Marca o pagamento como falho."""
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.utcnow()

    @property
    def is_pending(self) -> bool:
        """Verifica se está aguardando processamento."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Verifica se foi concluído."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_refunded(self) -> bool:
        """Verifica se foi reembolsado (total ou parcial)."""
        return self.status in (
            PaymentStatus.REFUNDED,
            PaymentStatus.PARTIALLY_REFUNDED,
        )

    @property
    def net_amount(self) -> Decimal:
        """Retorna valor líquido após reembolso (se houver)."""
        if self.refund_amount:
            return self.amount - self.refund_amount
        return self.amount
