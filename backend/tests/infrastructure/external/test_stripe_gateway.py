"""
Unit Tests for StripePaymentGateway
"""

import pytest
from unittest.mock import AsyncMock, patch
from decimal import Decimal
from uuid import uuid4

from src.infrastructure.external.stripe_gateway import StripePaymentGateway
from src.domain.interfaces.payment_gateway import (
    PaymentIntentResult,
    RefundResult,
    ConnectedAccountResult,
    TransferResult,
)

@pytest.fixture
def gateway():
    with patch("src.infrastructure.external.stripe_gateway.settings") as mock_settings:
        mock_settings.stripe_secret_key = "sk_test_dummy"
        import stripe
        stripe.api_key = "sk_test_dummy"
        yield StripePaymentGateway()

@pytest.mark.asyncio
async def test_create_payment_intent(gateway):
    with patch("stripe.PaymentIntent.create_async", new_callable=AsyncMock) as mock_create:
        mock_create.return_value.id = "pi_123"
        mock_create.return_value.client_secret = "secret_123"
        mock_create.return_value.status = "requires_payment_method"

        result = await gateway.create_payment_intent(
            amount=Decimal("100.00"),
            currency="brl",
            transfer_group="group_1",
            metadata={"test": "data"}
        )

        assert isinstance(result, PaymentIntentResult)
        assert result.payment_intent_id == "pi_123"
        assert result.client_secret == "secret_123"
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_confirm_payment_intent(gateway):
    with patch("stripe.PaymentIntent.confirm_async", new_callable=AsyncMock) as mock_confirm:
        mock_confirm.return_value.id = "pi_123"
        mock_confirm.return_value.client_secret = "secret_123"
        mock_confirm.return_value.status = "succeeded"

        result = await gateway.confirm_payment_intent("pi_123")

        assert isinstance(result, PaymentIntentResult)
        assert result.status == "succeeded"
        mock_confirm.assert_called_once_with("pi_123")

@pytest.mark.asyncio
async def test_process_refund(gateway):
    with patch("stripe.Refund.create_async", new_callable=AsyncMock) as mock_refund:
        mock_refund.return_value.id = "re_123"
        mock_refund.return_value.status = "succeeded"
        mock_refund.return_value.amount = 5000 # cents

        result = await gateway.process_refund(
            payment_intent_id="pi_123",
            amount=Decimal("50.00"),
            reason="test reason"
        )

        assert isinstance(result, RefundResult)
        assert result.refund_id == "re_123"
        assert result.amount == Decimal("50.00")
        mock_refund.assert_called_once()

@pytest.mark.asyncio
async def test_create_connected_account(gateway):
    with patch("stripe.Account.create_async", new_callable=AsyncMock) as mock_account:
        mock_account.return_value.id = "acct_123"
        
        instructor_id = uuid4()
        result = await gateway.create_connected_account(
            email="test@example.com",
            instructor_id=instructor_id
        )

        assert isinstance(result, ConnectedAccountResult)
        assert result.account_id == "acct_123"
        mock_account.assert_called_once()
        args, kwargs = mock_account.call_args
        assert kwargs["metadata"]["instructor_id"] == str(instructor_id)

@pytest.mark.asyncio
async def test_create_transfer(gateway):
    with patch("stripe.Transfer.create_async", new_callable=AsyncMock) as mock_transfer:
        mock_transfer.return_value.id = "tr_123"
        mock_transfer.return_value.amount = 8000
        mock_transfer.return_value.object = "transfer"

        result = await gateway.create_transfer(
            amount=Decimal("80.00"),
            destination_account_id="acct_123",
            transfer_group="group_1"
        )

        assert isinstance(result, TransferResult)
        assert result.transfer_id == "tr_123"
        assert result.amount == Decimal("80.00")
        mock_transfer.assert_called_once()
