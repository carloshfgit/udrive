"""
Testes unitários para lógica de reembolso na entidade Payment.
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus


class TestPaymentRefund:
    """Testes para process_refund e can_refund da entidade Payment."""

    def _make_payment(
        self,
        amount: Decimal = Decimal("100.00"),
        status: PaymentStatus = PaymentStatus.COMPLETED,
    ) -> Payment:
        """Helper para criar Payment com valores padrão."""
        return Payment(
            scheduling_id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            amount=amount,
            platform_fee_percentage=Decimal("20.00"),
            status=status,
            gateway_payment_id="mp_payment_123",
        )

    # ===== can_refund =====

    def test_can_refund_completed(self):
        """COMPLETED pode ser reembolsado."""
        payment = self._make_payment(status=PaymentStatus.COMPLETED)
        assert payment.can_refund() is True

    def test_cannot_refund_pending(self):
        """PENDING não pode ser reembolsado."""
        payment = self._make_payment(status=PaymentStatus.PENDING)
        assert payment.can_refund() is False

    def test_cannot_refund_processing(self):
        """PROCESSING não pode ser reembolsado."""
        payment = self._make_payment(status=PaymentStatus.PROCESSING)
        assert payment.can_refund() is False

    def test_cannot_refund_failed(self):
        """FAILED não pode ser reembolsado."""
        payment = self._make_payment(status=PaymentStatus.FAILED)
        assert payment.can_refund() is False

    def test_cannot_refund_already_refunded(self):
        """REFUNDED não pode ser reembolsado novamente."""
        payment = self._make_payment(status=PaymentStatus.REFUNDED)
        assert payment.can_refund() is False

    def test_cannot_refund_partially_refunded(self):
        """PARTIALLY_REFUNDED não pode ser reembolsado novamente."""
        payment = self._make_payment(status=PaymentStatus.PARTIALLY_REFUNDED)
        assert payment.can_refund() is False

    # ===== process_refund — Percentuais =====

    def test_full_refund_100_percent(self):
        """Reembolso de 100% muda status para REFUNDED."""
        payment = self._make_payment(amount=Decimal("100.00"))
        refund_amount = payment.process_refund(100)

        assert refund_amount == Decimal("100.00")
        assert payment.status == PaymentStatus.REFUNDED
        assert payment.refund_amount == Decimal("100.00")
        assert payment.refunded_at is not None

    def test_partial_refund_50_percent(self):
        """Reembolso de 50% muda status para PARTIALLY_REFUNDED."""
        payment = self._make_payment(amount=Decimal("100.00"))
        refund_amount = payment.process_refund(50)

        assert refund_amount == Decimal("50.00")
        assert payment.status == PaymentStatus.PARTIALLY_REFUNDED
        assert payment.refund_amount == Decimal("50.00")
        assert payment.refunded_at is not None

    def test_partial_refund_with_odd_amount(self):
        """Reembolso parcial arredondado corretamente."""
        payment = self._make_payment(amount=Decimal("89.90"))
        refund_amount = payment.process_refund(50)

        assert refund_amount == Decimal("44.95")
        assert payment.status == PaymentStatus.PARTIALLY_REFUNDED

    # ===== process_refund — Erros =====

    def test_refund_raises_on_non_completed_status(self):
        """process_refund lança ValueError se não estiver COMPLETED."""
        payment = self._make_payment(status=PaymentStatus.PENDING)
        with pytest.raises(ValueError, match="não pode ser reembolsado"):
            payment.process_refund(100)

    def test_refund_raises_on_invalid_percentage_negative(self):
        """process_refund lança ValueError para percentual negativo."""
        payment = self._make_payment()
        with pytest.raises(ValueError, match="entre 0 e 100"):
            payment.process_refund(-10)

    def test_refund_raises_on_invalid_percentage_over_100(self):
        """process_refund lança ValueError para percentual acima de 100."""
        payment = self._make_payment()
        with pytest.raises(ValueError, match="entre 0 e 100"):
            payment.process_refund(150)

    # ===== net_amount =====

    def test_net_amount_without_refund(self):
        """net_amount retorna valor total se sem reembolso."""
        payment = self._make_payment(amount=Decimal("100.00"))
        assert payment.net_amount == Decimal("100.00")

    def test_net_amount_after_partial_refund(self):
        """net_amount retorna valor líquido após reembolso parcial."""
        payment = self._make_payment(amount=Decimal("100.00"))
        payment.process_refund(50)
        assert payment.net_amount == Decimal("50.00")

    def test_net_amount_after_full_refund(self):
        """net_amount retorna 0 após reembolso total."""
        payment = self._make_payment(amount=Decimal("100.00"))
        payment.process_refund(100)
        assert payment.net_amount == Decimal("0.00")
