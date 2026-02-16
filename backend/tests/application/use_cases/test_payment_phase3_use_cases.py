"""
Mercado Pago Integration — Phase 3 Tests

Testes para CreateCheckoutUseCase e HandlePaymentWebhookUseCase.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from src.application.dtos.payment_dtos import CreateCheckoutDTO, WebhookNotificationDTO
from src.application.use_cases.payment.create_checkout import CreateCheckoutUseCase
from src.application.use_cases.payment.handle_payment_webhook import HandlePaymentWebhookUseCase
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    SchedulingNotFoundException,
    GatewayAccountNotConnectedException,
    PaymentAlreadyProcessedException
)
from src.domain.interfaces.payment_gateway import CheckoutResult, PaymentStatusResult


@pytest.fixture
def mock_repositories():
    return {
        "scheduling": AsyncMock(),
        "payment": AsyncMock(),
        "transaction": AsyncMock(),
        "instructor": AsyncMock(),
    }


@pytest.fixture
def mock_gateway():
    return AsyncMock()


@pytest.fixture
def mock_calculate_split():
    mock = MagicMock()
    mock.execute.return_value = MagicMock(
        platform_fee_percentage=Decimal("20.00"),
        platform_fee_amount=Decimal("20.00"),
        instructor_amount=Decimal("80.00")
    )
    return mock


@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.mp_redirect_uri = "http://api.godrive.com.br/payments/mercadopago/oauth"
    return mock


class TestCreateCheckoutUseCase:
    @pytest.mark.asyncio
    async def test_create_checkout_success(
        self, mock_repositories, mock_gateway, mock_calculate_split, mock_settings
    ):
        # Arrange
        scheduling_id = uuid4()
        instructor_id = uuid4()
        student_id = uuid4()
        
        scheduling = MagicMock()
        scheduling.id = scheduling_id
        scheduling.instructor_id = instructor_id
        scheduling.price = Decimal("100.00")
        scheduling.scheduled_datetime = datetime.now()
        mock_repositories["scheduling"].get_by_id.return_value = scheduling
        
        mock_repositories["payment"].get_by_scheduling_id.return_value = None
        
        instructor = MagicMock()
        instructor.has_mp_account = True
        instructor.mp_access_token = "fake-token"
        mock_repositories["instructor"].get_by_user_id.return_value = instructor
        
        mock_repositories["payment"].create.side_effect = lambda p: p
        mock_repositories["payment"].update.side_effect = lambda p: p
        
        mock_gateway.create_checkout.return_value = CheckoutResult(
            preference_id="pref-123",
            checkout_url="http://mp.com/checkout",
            sandbox_url="http://mp.com/sandbox"
        )
        
        use_case = CreateCheckoutUseCase(
            scheduling_repository=mock_repositories["scheduling"],
            payment_repository=mock_repositories["payment"],
            transaction_repository=mock_repositories["transaction"],
            instructor_repository=mock_repositories["instructor"],
            payment_gateway=mock_gateway,
            calculate_split_use_case=mock_calculate_split,
            settings=mock_settings
        )
        
        dto = CreateCheckoutDTO(
            scheduling_id=scheduling_id,
            student_id=student_id,
            student_email="student@example.com"
        )
        
        # Act
        result = await use_case.execute(dto)
        
        # Assert
        assert result.preference_id == "pref-123"
        assert result.checkout_url == "http://mp.com/checkout"
        assert result.status == PaymentStatus.PROCESSING.value
        mock_gateway.create_checkout.assert_called_once()
        mock_repositories["payment"].create.assert_called_once()
        mock_repositories["transaction"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_checkout_scheduling_not_found(self, mock_repositories):
        mock_repositories["scheduling"].get_by_id.return_value = None
        use_case = CreateCheckoutUseCase(
            **{k + "_repository": v for k, v in mock_repositories.items()},
            payment_gateway=MagicMock(),
            calculate_split_use_case=MagicMock(),
            settings=MagicMock()
        )
        with pytest.raises(SchedulingNotFoundException):
            await use_case.execute(CreateCheckoutDTO(uuid4(), uuid4()))


class TestHandlePaymentWebhookUseCase:
    @pytest.mark.asyncio
    async def test_handle_webhook_approved(self, mock_repositories, mock_gateway):
        # Arrange
        payment_id = uuid4()
        scheduling_id = uuid4()
        instructor_id = uuid4()
        mp_payment_id = "555666777"
        
        payment = MagicMock()
        payment.id = payment_id
        payment.scheduling_id = scheduling_id
        payment.instructor_id = instructor_id
        payment.amount = Decimal("100.00")
        payment.status = PaymentStatus.PROCESSING
        payment.gateway_preference_id = "pref-123"
        mock_repositories["payment"].get_by_gateway_payment_id.return_value = payment
        
        instructor = MagicMock()
        instructor.has_mp_account = True
        instructor.mp_access_token = "fake-token"
        mock_repositories["instructor"].get_by_user_id.return_value = instructor
        
        mock_gateway.get_payment_status.return_value = PaymentStatusResult(
            payment_id=mp_payment_id,
            status="approved",
            status_detail="accredited",
            payer_email="student@example.com"
        )
        
        scheduling = MagicMock()
        scheduling.id = scheduling_id
        scheduling.can_confirm = True
        mock_repositories["scheduling"].get_by_id.return_value = scheduling
        
        use_case = HandlePaymentWebhookUseCase(
            payment_repository=mock_repositories["payment"],
            scheduling_repository=mock_repositories["scheduling"],
            transaction_repository=mock_repositories["transaction"],
            instructor_repository=mock_repositories["instructor"],
            payment_gateway=mock_gateway
        )
        
        dto = WebhookNotificationDTO(
            notification_id=1,
            notification_type="payment",
            action="payment.updated",
            data_id=mp_payment_id
        )
        
        # Act
        await use_case.execute(dto)
        
        # Assert
        payment.mark_completed.assert_called_once()
        mock_repositories["payment"].update.assert_called_once_with(payment)
        scheduling.confirm.assert_called_once()
        mock_repositories["scheduling"].update.assert_called_once_with(scheduling)
        mock_repositories["transaction"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_webhook_idempotency(self, mock_repositories, mock_gateway):
        # Arrange
        payment = MagicMock()
        payment.status = PaymentStatus.COMPLETED
        mock_repositories["payment"].get_by_gateway_payment_id.return_value = payment
        
        instructor = MagicMock()
        instructor.has_mp_account = True
        mock_repositories["instructor"].get_by_user_id.return_value = instructor
        
        mock_gateway.get_payment_status.return_value = PaymentStatusResult(
            payment_id="123",
            status="approved",
            status_detail="accredited"
        )
        
        use_case = HandlePaymentWebhookUseCase(
            payment_repository=mock_repositories["payment"],
            scheduling_repository=mock_repositories["scheduling"],
            transaction_repository=mock_repositories["transaction"],
            instructor_repository=mock_repositories["instructor"],
            payment_gateway=mock_gateway
        )
        
        # Act
        await use_case.execute(WebhookNotificationDTO(1, "payment", "payment.updated", "123"))
        
        # Assert
        # should return early and not call update
        assert mock_repositories["payment"].update.call_count == 0
