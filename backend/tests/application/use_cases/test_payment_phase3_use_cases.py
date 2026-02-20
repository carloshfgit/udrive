"""
Mercado Pago Integration — Phase 3 Tests

Testes para CreateCheckoutUseCase e HandlePaymentWebhookUseCase.
Inclui cenários multi-item com preference_group_id.
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
    MixedInstructorsException,
    SchedulingNotFoundException,
    GatewayAccountNotConnectedException,
    PaymentAlreadyProcessedException
)
from src.domain.interfaces.payment_gateway import CheckoutResult, PaymentStatusResult


@pytest.fixture(autouse=True)
def _bypass_decrypt(monkeypatch):
    """Bypass de criptografia: decrypt_token retorna o valor inalterado."""
    monkeypatch.setattr(
        "src.application.use_cases.payment.create_checkout.decrypt_token",
        lambda t: t,
    )
    monkeypatch.setattr(
        "src.application.use_cases.payment.handle_payment_webhook.decrypt_token",
        lambda t: t,
    )


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


def _make_scheduling(instructor_id, price=Decimal("100.00"), duration=60):
    """Helper para criar um scheduling mockado."""
    scheduling = MagicMock()
    scheduling.id = uuid4()
    scheduling.instructor_id = instructor_id
    scheduling.price = price
    scheduling.duration_minutes = duration
    scheduling.scheduled_datetime = datetime.now()
    scheduling.is_cancelled = False
    return scheduling


class TestCreateCheckoutUseCase:
    @pytest.mark.asyncio
    async def test_create_checkout_single_item_success(
        self, mock_repositories, mock_gateway, mock_calculate_split, mock_settings
    ):
        """Checkout com um único agendamento (backward compat)."""
        instructor_id = uuid4()
        student_id = uuid4()
        scheduling = _make_scheduling(instructor_id)

        mock_repositories["scheduling"].get_by_id.return_value = scheduling
        mock_repositories["payment"].get_by_scheduling_id.return_value = None

        instructor = MagicMock()
        instructor.has_mp_account = True
        instructor.mp_access_token = "fake-token"
        instructor.hourly_rate = Decimal("80.00")
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
            scheduling_ids=[scheduling.id],
            student_id=student_id,
            student_email="student@example.com"
        )

        result = await use_case.execute(dto)

        assert result.preference_id == "pref-123"
        assert result.checkout_url == "http://mp.com/checkout"
        assert result.status == PaymentStatus.PROCESSING.value
        mock_gateway.create_checkout.assert_called_once()
        mock_repositories["payment"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_checkout_multi_item_success(
        self, mock_repositories, mock_gateway, mock_calculate_split, mock_settings
    ):
        """Checkout com múltiplos agendamentos do mesmo instrutor."""
        instructor_id = uuid4()
        student_id = uuid4()
        scheduling_1 = _make_scheduling(instructor_id, Decimal("100.00"))
        scheduling_2 = _make_scheduling(instructor_id, Decimal("120.00"))

        mock_repositories["scheduling"].get_by_id.side_effect = lambda sid: {
            scheduling_1.id: scheduling_1,
            scheduling_2.id: scheduling_2,
        }.get(sid)

        mock_repositories["payment"].get_by_scheduling_id.return_value = None

        instructor = MagicMock()
        instructor.has_mp_account = True
        instructor.mp_access_token = "fake-token"
        instructor.hourly_rate = Decimal("80.00")
        mock_repositories["instructor"].get_by_user_id.return_value = instructor

        mock_repositories["payment"].create.side_effect = lambda p: p
        mock_repositories["payment"].update.side_effect = lambda p: p

        mock_gateway.create_checkout.return_value = CheckoutResult(
            preference_id="pref-multi",
            checkout_url="http://mp.com/checkout-multi",
            sandbox_url="http://mp.com/sandbox-multi"
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
            scheduling_ids=[scheduling_1.id, scheduling_2.id],
            student_id=student_id,
        )

        result = await use_case.execute(dto)

        assert result.preference_id == "pref-multi"
        assert result.status == PaymentStatus.PROCESSING.value
        # Deve criar 2 payments (um por scheduling)
        assert mock_repositories["payment"].create.call_count == 2
        # Deve atualizar 2 payments com preference_id
        assert mock_repositories["payment"].update.call_count == 2
        # Items enviados ao MP devem conter 2 itens
        call_kwargs = mock_gateway.create_checkout.call_args.kwargs
        assert len(call_kwargs["items"]) == 2

    @pytest.mark.asyncio
    async def test_create_checkout_mixed_instructors_raises(
        self, mock_repositories, mock_gateway, mock_calculate_split, mock_settings
    ):
        """Tentativa de checkout com instrutores diferentes deve falhar."""
        instructor_1 = uuid4()
        instructor_2 = uuid4()
        scheduling_1 = _make_scheduling(instructor_1)
        scheduling_2 = _make_scheduling(instructor_2)

        mock_repositories["scheduling"].get_by_id.side_effect = lambda sid: {
            scheduling_1.id: scheduling_1,
            scheduling_2.id: scheduling_2,
        }.get(sid)

        mock_repositories["payment"].get_by_scheduling_id.return_value = None

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
            scheduling_ids=[scheduling_1.id, scheduling_2.id],
            student_id=uuid4(),
        )

        with pytest.raises(MixedInstructorsException):
            await use_case.execute(dto)

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
            await use_case.execute(CreateCheckoutDTO(
                scheduling_ids=[uuid4()],
                student_id=uuid4()
            ))

    @pytest.mark.asyncio
    async def test_create_checkout_empty_ids_raises(self, mock_repositories):
        """Lista vazia de scheduling_ids deve lançar exceção."""
        use_case = CreateCheckoutUseCase(
            **{k + "_repository": v for k, v in mock_repositories.items()},
            payment_gateway=MagicMock(),
            calculate_split_use_case=MagicMock(),
            settings=MagicMock()
        )
        with pytest.raises(SchedulingNotFoundException):
            await use_case.execute(CreateCheckoutDTO(
                scheduling_ids=[],
                student_id=uuid4()
            ))


class TestHandlePaymentWebhookUseCase:
    @pytest.mark.asyncio
    async def test_handle_webhook_approved_single(self, mock_repositories, mock_gateway):
        """Webhook approved com payment sem grupo (legado)."""
        scheduling_id = uuid4()
        instructor_id = uuid4()
        mp_payment_id = "555666777"

        payment = MagicMock()
        payment.id = uuid4()
        payment.scheduling_id = scheduling_id
        payment.instructor_id = instructor_id
        payment.amount = Decimal("100.00")
        payment.status = PaymentStatus.PROCESSING
        payment.gateway_preference_id = "pref-123"
        payment.preference_group_id = None  # Legado: sem grupo
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
        scheduling.can_confirm = MagicMock(return_value=True)
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

        await use_case.execute(dto)

        payment.mark_completed.assert_called_once()
        mock_repositories["payment"].update.assert_called_once_with(payment)
        scheduling.confirm.assert_called_once()
        mock_repositories["scheduling"].update.assert_called_once_with(scheduling)
        mock_repositories["transaction"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_webhook_approved_multi_item(self, mock_repositories, mock_gateway):
        """Webhook approved com group: todos os payments e schedulings atualizados."""
        group_id = uuid4()
        instructor_id = uuid4()
        mp_payment_id = "888999000"

        # 2 payments do mesmo grupo
        payment_1 = MagicMock()
        payment_1.id = uuid4()
        payment_1.scheduling_id = uuid4()
        payment_1.instructor_id = instructor_id
        payment_1.amount = Decimal("100.00")
        payment_1.status = PaymentStatus.PROCESSING
        payment_1.gateway_preference_id = "pref-group"
        payment_1.preference_group_id = group_id
        payment_1.student_id = uuid4()

        payment_2 = MagicMock()
        payment_2.id = uuid4()
        payment_2.scheduling_id = uuid4()
        payment_2.instructor_id = instructor_id
        payment_2.amount = Decimal("120.00")
        payment_2.status = PaymentStatus.PROCESSING
        payment_2.gateway_preference_id = "pref-group"
        payment_2.preference_group_id = group_id
        payment_2.student_id = payment_1.student_id

        mock_repositories["payment"].get_by_gateway_payment_id.return_value = payment_1
        mock_repositories["payment"].get_by_preference_group_id.return_value = [payment_1, payment_2]

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

        scheduling_1 = MagicMock()
        scheduling_1.id = payment_1.scheduling_id
        scheduling_1.can_confirm = MagicMock(return_value=True)

        scheduling_2 = MagicMock()
        scheduling_2.id = payment_2.scheduling_id
        scheduling_2.can_confirm = MagicMock(return_value=True)

        mock_repositories["scheduling"].get_by_id.side_effect = lambda sid: {
            scheduling_1.id: scheduling_1,
            scheduling_2.id: scheduling_2,
        }.get(sid)

        use_case = HandlePaymentWebhookUseCase(
            payment_repository=mock_repositories["payment"],
            scheduling_repository=mock_repositories["scheduling"],
            transaction_repository=mock_repositories["transaction"],
            instructor_repository=mock_repositories["instructor"],
            payment_gateway=mock_gateway
        )

        dto = WebhookNotificationDTO(
            notification_id=2,
            notification_type="payment",
            action="payment.updated",
            data_id=mp_payment_id
        )

        await use_case.execute(dto)

        # Ambos payments marcados como completed
        payment_1.mark_completed.assert_called_once()
        payment_2.mark_completed.assert_called_once()
        # Ambos payments atualizados
        assert mock_repositories["payment"].update.call_count == 2
        # Ambos schedulings confirmados
        scheduling_1.confirm.assert_called_once()
        scheduling_2.confirm.assert_called_once()
        assert mock_repositories["scheduling"].update.call_count == 2
        # 2 transactions criadas
        assert mock_repositories["transaction"].create.call_count == 2

    @pytest.mark.asyncio
    async def test_handle_webhook_idempotency(self, mock_repositories, mock_gateway):
        """Se todos os payments já estão COMPLETED, não deve atualizar nada."""
        payment = MagicMock()
        payment.status = PaymentStatus.COMPLETED
        payment.preference_group_id = uuid4()
        mock_repositories["payment"].get_by_gateway_payment_id.return_value = payment
        mock_repositories["payment"].get_by_preference_group_id.return_value = [payment]

        instructor = MagicMock()
        instructor.has_mp_account = True
        instructor.mp_access_token = "fake-token"
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

        await use_case.execute(WebhookNotificationDTO(1, "payment", "payment.updated", "123"))

        assert mock_repositories["payment"].update.call_count == 0
