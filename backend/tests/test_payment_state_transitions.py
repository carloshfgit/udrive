"""
Tests for Payment Entity State Transitions

Testes unitários para validar as transições de estado do Payment
no modelo de custódia (escrow).
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus


# =============================================================================
# Fixtures
# =============================================================================


def make_payment(**kwargs) -> Payment:
    """Factory helper para criar Payment com valores padrão."""
    defaults = {
        "scheduling_id": uuid4(),
        "student_id": uuid4(),
        "instructor_id": uuid4(),
        "amount": Decimal("100.00"),
    }
    defaults.update(kwargs)
    return Payment(**defaults)


# =============================================================================
# Testes de Transição: PENDING → PROCESSING
# =============================================================================


class TestMarkProcessing:
    def test_pending_to_processing(self):
        payment = make_payment()
        assert payment.status == PaymentStatus.PENDING

        payment.mark_processing("pi_test_123")

        assert payment.status == PaymentStatus.PROCESSING
        assert payment.stripe_payment_intent_id == "pi_test_123"
        assert payment.updated_at is not None

    def test_cannot_process_from_non_pending(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")

        with pytest.raises(ValueError, match="não pode ser processado"):
            payment.mark_processing("pi_test_456")


# =============================================================================
# Testes de Transição: PROCESSING → HELD
# =============================================================================


class TestMarkHeld:
    def test_processing_to_held(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")

        payment.mark_held()

        assert payment.status == PaymentStatus.HELD
        assert payment.updated_at is not None

    def test_cannot_hold_from_pending(self):
        payment = make_payment()

        with pytest.raises(ValueError, match="não pode ser retido"):
            payment.mark_held()

    def test_cannot_hold_from_completed(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()
        payment.mark_completed("tr_test_123")

        with pytest.raises(ValueError, match="não pode ser retido"):
            payment.mark_held()


# =============================================================================
# Testes de Transição: HELD → COMPLETED
# =============================================================================


class TestMarkCompleted:
    def test_held_to_completed(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()

        payment.mark_completed("tr_test_456")

        assert payment.status == PaymentStatus.COMPLETED
        assert payment.stripe_transfer_id == "tr_test_456"
        assert payment.updated_at is not None

    def test_cannot_complete_from_processing(self):
        """Escrow model: must go through HELD first."""
        payment = make_payment()
        payment.mark_processing("pi_test_123")

        with pytest.raises(ValueError, match="não pode ser concluído"):
            payment.mark_completed("tr_test_456")

    def test_cannot_complete_from_pending(self):
        payment = make_payment()

        with pytest.raises(ValueError, match="não pode ser concluído"):
            payment.mark_completed("tr_test_456")


# =============================================================================
# Testes de Transição: HELD → DISPUTED
# =============================================================================


class TestMarkDisputed:
    def test_held_to_disputed(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()

        payment.mark_disputed()

        assert payment.status == PaymentStatus.DISPUTED
        assert payment.updated_at is not None

    def test_cannot_dispute_from_processing(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")

        with pytest.raises(ValueError, match="não pode ser disputado"):
            payment.mark_disputed()

    def test_cannot_dispute_from_pending(self):
        payment = make_payment()

        with pytest.raises(ValueError, match="não pode ser disputado"):
            payment.mark_disputed()


# =============================================================================
# Testes de can_refund
# =============================================================================


class TestCanRefund:
    def test_can_refund_when_completed(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()
        payment.mark_completed("tr_test_456")

        assert payment.can_refund() is True

    def test_can_refund_when_held(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()

        assert payment.can_refund() is True

    def test_cannot_refund_when_pending(self):
        payment = make_payment()
        assert payment.can_refund() is False

    def test_cannot_refund_when_processing(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        assert payment.can_refund() is False

    def test_cannot_refund_when_failed(self):
        payment = make_payment()
        payment.mark_failed()
        assert payment.can_refund() is False


# =============================================================================
# Testes de Propriedades
# =============================================================================


class TestPaymentProperties:
    def test_is_held(self):
        payment = make_payment()
        payment.mark_processing("pi_test_123")
        payment.mark_held()

        assert payment.is_held is True
        assert payment.is_completed is False
        assert payment.is_pending is False

    def test_transfer_group(self):
        payment = make_payment()
        assert payment.transfer_group is None

        payment.transfer_group = f"payment_{payment.id}"
        assert payment.transfer_group is not None
        assert payment.transfer_group.startswith("payment_")


# =============================================================================
# Testes de Fluxo Completo (Happy Path)
# =============================================================================


class TestFullEscrowFlow:
    def test_full_flow_pending_to_completed(self):
        """Simula o fluxo completo: PENDING → PROCESSING → HELD → COMPLETED."""
        payment = make_payment()
        assert payment.status == PaymentStatus.PENDING

        # 1. Processar pagamento
        payment.mark_processing("pi_live_123")
        assert payment.status == PaymentStatus.PROCESSING

        # 2. Webhook confirma → HELD (escrow)
        payment.mark_held()
        assert payment.status == PaymentStatus.HELD

        # 3. Aula concluída → Transfer → COMPLETED
        payment.mark_completed("tr_live_456")
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.stripe_payment_intent_id == "pi_live_123"
        assert payment.stripe_transfer_id == "tr_live_456"

    def test_flow_with_dispute(self):
        """Simula fluxo com disputa: PENDING → PROCESSING → HELD → DISPUTED."""
        payment = make_payment()

        payment.mark_processing("pi_live_789")
        payment.mark_held()
        payment.mark_disputed()

        assert payment.status == PaymentStatus.DISPUTED

    def test_flow_with_refund_from_held(self):
        """Simula reembolso diretamente do estado HELD."""
        payment = make_payment()

        payment.mark_processing("pi_live_abc")
        payment.mark_held()

        refund_amount = payment.process_refund(100)
        assert refund_amount == Decimal("100.00")
        assert payment.status == PaymentStatus.REFUNDED
