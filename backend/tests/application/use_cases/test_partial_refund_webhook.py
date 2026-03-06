"""
Testes unitários para o tratamento de webhook `partially_refunded`
no HandlePaymentWebhookUseCase.

Cobre: idempotência (refund_id já mapeado), associação por valor,
múltiplos refunds, candidato não encontrado, e regressão do _handle_refunded.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.application.use_cases.payment.handle_payment_webhook import (
    HandlePaymentWebhookUseCase,
)
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.interfaces.payment_gateway import PaymentStatusResult


# === Fixtures ===


@pytest.fixture(autouse=True)
def _bypass_decrypt(monkeypatch):
    """Bypass de criptografia: decrypt_token retorna o valor inalterado."""
    monkeypatch.setattr(
        "src.application.use_cases.payment.handle_payment_webhook.decrypt_token",
        lambda t: t,
    )


@pytest.fixture
def repos():
    return {
        "payment": AsyncMock(),
        "scheduling": AsyncMock(),
        "transaction": AsyncMock(),
        "instructor": AsyncMock(),
    }


@pytest.fixture
def gateway():
    return AsyncMock()


@pytest.fixture
def use_case(repos, gateway):
    return HandlePaymentWebhookUseCase(
        payment_repository=repos["payment"],
        scheduling_repository=repos["scheduling"],
        transaction_repository=repos["transaction"],
        instructor_repository=repos["instructor"],
        payment_gateway=gateway,
    )


# === Helpers ===

GROUP_ID = uuid4()


def _make_payment(
    amount: Decimal = Decimal("100.00"),
    status: PaymentStatus = PaymentStatus.COMPLETED,
    mp_refund_id: str | None = None,
    gateway_payment_id: str = "mp_pay_999",
    preference_group_id=GROUP_ID,
) -> Payment:
    return Payment(
        scheduling_id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        amount=amount,
        platform_fee_percentage=Decimal("20.00"),
        status=status,
        gateway_payment_id=gateway_payment_id,
        gateway_preference_id="pref-123",
        preference_group_id=preference_group_id,
        mp_refund_id=mp_refund_id,
    )


def _make_instructor():
    profile = MagicMock()
    profile.has_mp_account = True
    profile.mp_access_token = "fake-token"
    return profile


def _setup_gateway_partially_refunded(gateway, refunds: list[dict]):
    """Configura gateway para retornar status partially_refunded e lista de refunds."""
    gateway.get_payment_status.return_value = PaymentStatusResult(
        payment_id="mp_pay_999",
        status="approved",
        status_detail="partially_refunded",
        payer_email="student@test.com",
    )
    gateway.get_refunds.return_value = refunds


def _make_webhook_dto(mp_payment_id: str = "mp_pay_999") -> WebhookNotificationDTO:
    return WebhookNotificationDTO(
        notification_id=1,
        notification_type="payment",
        action="payment.updated",
        data_id=mp_payment_id,
        user_id=None,
    )


# === Testes ===


class TestPartialRefundIdempotent:
    """Webhook chega mas Payment já tem o mp_refund_id → nenhuma atualização."""

    @pytest.mark.asyncio
    async def test_partial_refund_idempotent(self, repos, gateway, use_case):
        # Payment já processado pela Fase 3 (RefundSinglePaymentUseCase)
        payment = _make_payment(
            amount=Decimal("100.00"),
            status=PaymentStatus.REFUNDED,
            mp_refund_id="refund_001",
        )

        repos["payment"].get_by_gateway_payment_id.return_value = payment
        repos["payment"].get_by_preference_group_id.return_value = [payment]
        repos["instructor"].get_by_user_id.return_value = _make_instructor()

        _setup_gateway_partially_refunded(
            gateway, [{"id": "refund_001", "amount": 100.00, "status": "approved"}]
        )

        await use_case.execute(_make_webhook_dto())

        # Nenhum update deve ter sido chamado (idempotência)
        repos["payment"].update.assert_not_called()


class TestPartialRefundAssociateByAmount:
    """Webhook com 1 refund que não está mapeado → associa pelo valor."""

    @pytest.mark.asyncio
    async def test_associates_refund_to_correct_payment(self, repos, gateway, use_case):
        # Grupo com 2 payments: P1 (R$100) e P2 (R$150), ambos COMPLETED
        p1 = _make_payment(amount=Decimal("100.00"))
        p2 = _make_payment(amount=Decimal("150.00"))

        repos["payment"].get_by_gateway_payment_id.return_value = p1
        repos["payment"].get_by_preference_group_id.return_value = [p1, p2]
        repos["instructor"].get_by_user_id.return_value = _make_instructor()

        # Refund de R$100 → deve bater com P1
        _setup_gateway_partially_refunded(
            gateway, [{"id": "refund_xyz", "amount": 100.00, "status": "approved"}]
        )

        await use_case.execute(_make_webhook_dto())

        # P1 deve ter sido atualizado com o refund_id
        assert p1.mp_refund_id == "refund_xyz"
        assert p1.status == PaymentStatus.REFUNDED
        repos["payment"].update.assert_called_once_with(p1)

        # P2 deve permanecer inalterado
        assert p2.mp_refund_id is None
        assert p2.status == PaymentStatus.COMPLETED


class TestPartialRefundMultipleRefunds:
    """Webhook com 2 refunds, encontra 2 Payments diferentes."""

    @pytest.mark.asyncio
    async def test_multiple_refunds_associate_correctly(self, repos, gateway, use_case):
        p1 = _make_payment(amount=Decimal("100.00"))
        p2 = _make_payment(amount=Decimal("200.00"))
        p3 = _make_payment(amount=Decimal("150.00"))

        repos["payment"].get_by_gateway_payment_id.return_value = p1
        repos["payment"].get_by_preference_group_id.return_value = [p1, p2, p3]
        repos["instructor"].get_by_user_id.return_value = _make_instructor()

        _setup_gateway_partially_refunded(
            gateway,
            [
                {"id": "refund_a", "amount": 100.00, "status": "approved"},
                {"id": "refund_b", "amount": 200.00, "status": "approved"},
            ],
        )

        await use_case.execute(_make_webhook_dto())

        # P1 e P2 devem ter sido atualizados
        assert p1.mp_refund_id == "refund_a"
        assert p1.status == PaymentStatus.REFUNDED
        assert p2.mp_refund_id == "refund_b"
        assert p2.status == PaymentStatus.REFUNDED

        # P3 permanece inalterado
        assert p3.mp_refund_id is None
        assert p3.status == PaymentStatus.COMPLETED

        assert repos["payment"].update.call_count == 2


class TestPartialRefundNoCandidate:
    """Refund com valor que não bate com nenhum Payment COMPLETED → warning."""

    @pytest.mark.asyncio
    async def test_no_matching_payment_by_amount(self, repos, gateway, use_case):
        p1 = _make_payment(amount=Decimal("100.00"))

        repos["payment"].get_by_gateway_payment_id.return_value = p1
        repos["payment"].get_by_preference_group_id.return_value = [p1]
        repos["instructor"].get_by_user_id.return_value = _make_instructor()

        # Refund de R$999 não bate com nenhum Payment
        _setup_gateway_partially_refunded(
            gateway, [{"id": "refund_zzz", "amount": 999.00, "status": "approved"}]
        )

        await use_case.execute(_make_webhook_dto())

        # Nenhum update
        repos["payment"].update.assert_not_called()
        assert p1.mp_refund_id is None
        assert p1.status == PaymentStatus.COMPLETED


class TestHandleRefundedRegression:
    """Status 'refunded' (total) continua marcando todos como REFUNDED (regressão)."""

    @pytest.mark.asyncio
    async def test_full_refund_marks_all_payments(self, repos, gateway, use_case):
        p1 = _make_payment(amount=Decimal("100.00"))
        p2 = _make_payment(amount=Decimal("150.00"))

        repos["payment"].get_by_gateway_payment_id.return_value = p1
        repos["payment"].get_by_preference_group_id.return_value = [p1, p2]
        repos["instructor"].get_by_user_id.return_value = _make_instructor()

        # Status "refunded" (total), NÃO "partially_refunded"
        gateway.get_payment_status.return_value = PaymentStatusResult(
            payment_id="mp_pay_999",
            status="refunded",
            status_detail="refunded",
        )

        await use_case.execute(_make_webhook_dto())

        # _handle_refunded deve ter marcado ambos como REFUNDED
        assert p1.status == PaymentStatus.REFUNDED
        assert p2.status == PaymentStatus.REFUNDED
        assert repos["payment"].update.call_count == 2

        # get_refunds NÃO deve ter sido chamado (é caminho de _handle_refunded, não partial)
        gateway.get_refunds.assert_not_called()
