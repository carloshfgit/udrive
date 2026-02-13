"""
Tests for HandleStripeWebhookUseCase

Testes unitários para o caso de uso de processamento de webhooks do Stripe.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.use_cases.payment.handle_stripe_webhook import (
    HandleStripeWebhookUseCase,
)
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus


# =============================================================================
# Fixtures
# =============================================================================


def make_processing_payment(pi_id: str = "pi_test_123") -> Payment:
    """Cria Payment em PROCESSING."""
    payment = Payment(
        scheduling_id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        amount=Decimal("100.00"),
    )
    payment.mark_processing(pi_id)
    return payment


def make_held_payment(pi_id: str = "pi_test_123") -> Payment:
    """Cria Payment em HELD."""
    payment = make_processing_payment(pi_id)
    payment.mark_held()
    return payment


def make_completed_payment(pi_id: str = "pi_test_123") -> Payment:
    """Cria Payment em COMPLETED."""
    payment = make_held_payment(pi_id)
    payment.mark_completed("tr_test_456")
    return payment


def make_use_case(payment=None):
    """Cria HandleStripeWebhookUseCase com mock de repositório."""
    payment_repo = AsyncMock()
    payment_repo.get_by_stripe_payment_intent_id.return_value = payment

    uc = HandleStripeWebhookUseCase(payment_repository=payment_repo)
    return uc, payment_repo


# =============================================================================
# Testes: payment_intent.succeeded
# =============================================================================


class TestPaymentIntentSucceeded:
    @pytest.mark.asyncio
    async def test_marks_payment_as_held(self):
        """PI succeeded → Payment muda de PROCESSING para HELD."""
        payment = make_processing_payment("pi_success_123")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="payment_intent.succeeded",
            event_data={"id": "pi_success_123"},
        )

        assert result["status"] == "processed"
        assert result["new_status"] == "held"
        payment_repo.update.assert_called_once()
        updated = payment_repo.update.call_args[0][0]
        assert updated.status == PaymentStatus.HELD

    @pytest.mark.asyncio
    async def test_skips_if_already_held(self):
        """Se já está HELD, não tenta fazer transição novamente."""
        payment = make_held_payment("pi_already_held")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="payment_intent.succeeded",
            event_data={"id": "pi_already_held"},
        )

        assert result["status"] == "processed"
        assert "already in" in result["detail"]
        payment_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_payment_not_found(self):
        """PI de um Payment inexistente."""
        uc, _ = make_use_case(payment=None)

        result = await uc.execute(
            event_type="payment_intent.succeeded",
            event_data={"id": "pi_unknown_999"},
        )

        assert result["status"] == "processed"
        assert "not found" in result["detail"]


# =============================================================================
# Testes: payment_intent.payment_failed
# =============================================================================


class TestPaymentIntentFailed:
    @pytest.mark.asyncio
    async def test_marks_payment_as_failed(self):
        """PI failed → Payment muda de PROCESSING para FAILED."""
        payment = make_processing_payment("pi_fail_123")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="payment_intent.payment_failed",
            event_data={"id": "pi_fail_123"},
        )

        assert result["status"] == "processed"
        assert result["new_status"] == "failed"
        payment_repo.update.assert_called_once()
        updated = payment_repo.update.call_args[0][0]
        assert updated.status == PaymentStatus.FAILED

    @pytest.mark.asyncio
    async def test_skips_if_already_completed(self):
        """Se já está COMPLETED, não marca como FAILED."""
        payment = make_completed_payment("pi_already_done")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="payment_intent.payment_failed",
            event_data={"id": "pi_already_done"},
        )

        assert "already in" in result["detail"]
        payment_repo.update.assert_not_called()


# =============================================================================
# Testes: charge.refunded
# =============================================================================


class TestChargeRefunded:
    @pytest.mark.asyncio
    async def test_full_refund(self):
        """Reembolso total via Stripe → REFUNDED."""
        payment = make_held_payment("pi_refund_full")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="charge.refunded",
            event_data={
                "payment_intent": "pi_refund_full",
                "amount_refunded": 10000,  # R$100.00 em centavos
            },
        )

        assert result["status"] == "processed"
        payment_repo.update.assert_called_once()
        updated = payment_repo.update.call_args[0][0]
        assert updated.status == PaymentStatus.REFUNDED

    @pytest.mark.asyncio
    async def test_partial_refund(self):
        """Reembolso parcial via Stripe → PARTIALLY_REFUNDED."""
        payment = make_held_payment("pi_refund_partial")
        uc, payment_repo = make_use_case(payment)

        result = await uc.execute(
            event_type="charge.refunded",
            event_data={
                "payment_intent": "pi_refund_partial",
                "amount_refunded": 5000,  # R$50.00 em centavos
            },
        )

        assert result["status"] == "processed"
        payment_repo.update.assert_called_once()
        updated = payment_repo.update.call_args[0][0]
        assert updated.status == PaymentStatus.PARTIALLY_REFUNDED


# =============================================================================
# Testes: account.updated
# =============================================================================


class TestAccountUpdated:
    @pytest.mark.asyncio
    async def test_logs_account_update(self):
        """Account updated deve apenas logar, sem consultar Payment."""
        uc, payment_repo = make_use_case()

        result = await uc.execute(
            event_type="account.updated",
            event_data={
                "id": "acct_test_123",
                "charges_enabled": True,
                "payouts_enabled": True,
                "details_submitted": True,
            },
        )

        assert result["status"] == "processed"
        assert result["account_id"] == "acct_test_123"
        assert result["charges_enabled"] is True
        payment_repo.get_by_stripe_payment_intent_id.assert_not_called()


# =============================================================================
# Testes: Evento desconhecido
# =============================================================================


class TestUnknownEvent:
    @pytest.mark.asyncio
    async def test_unknown_event_ignored(self):
        """Evento desconhecido deve ser ignorado."""
        uc, _ = make_use_case()

        result = await uc.execute(
            event_type="invoice.paid",
            event_data={"id": "inv_123"},
        )

        assert result["status"] == "ignored"
        assert result["event_type"] == "invoice.paid"
