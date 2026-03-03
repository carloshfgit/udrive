"""
Testes unitários para ProcessRefundUseCase.

Usa mocks para repositórios e gateway para testar a lógica de
processamento de reembolso isoladamente.
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import uuid4

from src.application.dtos.payment_dtos import ProcessRefundDTO
from src.application.use_cases.payment.process_refund import ProcessRefundUseCase
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.exceptions import PaymentNotFoundException, RefundException
from src.domain.interfaces.payment_gateway import RefundResult


@pytest.fixture
def payment_repo():
    return AsyncMock()


@pytest.fixture
def transaction_repo():
    return AsyncMock()


@pytest.fixture
def instructor_repo():
    return AsyncMock()


@pytest.fixture
def gateway():
    return AsyncMock()


@pytest.fixture
def use_case(payment_repo, transaction_repo, instructor_repo, gateway):
    return ProcessRefundUseCase(
        payment_repository=payment_repo,
        transaction_repository=transaction_repo,
        instructor_repository=instructor_repo,
        payment_gateway=gateway,
    )


def _make_payment(
    amount: Decimal = Decimal("100.00"),
    status: PaymentStatus = PaymentStatus.COMPLETED,
) -> Payment:
    return Payment(
        scheduling_id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        amount=amount,
        platform_fee_percentage=Decimal("20.00"),
        status=status,
        gateway_payment_id="mp_payment_123",
    )


def _make_instructor_profile(has_mp: bool = True):
    """Cria mock de InstructorProfile com conta MP."""
    profile = MagicMock()
    profile.has_mp_account = has_mp
    profile.mp_access_token = "encrypted_token"
    return profile


class TestProcessRefundSuccess:
    """Testes de reembolso bem-sucedido."""

    @pytest.mark.asyncio
    async def test_full_refund(
        self, payment_repo, transaction_repo, instructor_repo, gateway, use_case
    ):
        """Reembolso total (100%) chama gateway e cria transaction."""
        payment = _make_payment()
        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="refund_123",
            amount=Decimal("100.00"),
            status="approved",
        )

        dto = ProcessRefundDTO(
            payment_id=payment.id,
            refund_percentage=100,
            reason="Cancelamento",
        )

        with patch(
            "src.application.use_cases.payment.process_refund.decrypt_token",
            return_value="decrypted_token",
        ):
            result = await use_case.execute(dto)

        assert result.refund_amount == Decimal("100.00")
        assert result.refund_percentage == 100
        assert result.status == "refunded"
        gateway.process_refund.assert_called_once()
        payment_repo.update.assert_called_once()
        transaction_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_partial_refund_50(
        self, payment_repo, transaction_repo, instructor_repo, gateway, use_case
    ):
        """Reembolso parcial (50%) calcula valor correto."""
        payment = _make_payment(amount=Decimal("100.00"))
        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="refund_456",
            amount=Decimal("50.00"),
            status="approved",
        )

        dto = ProcessRefundDTO(
            payment_id=payment.id,
            refund_percentage=50,
        )

        with patch(
            "src.application.use_cases.payment.process_refund.decrypt_token",
            return_value="decrypted_token",
        ):
            result = await use_case.execute(dto)

        assert result.refund_amount == Decimal("50.00")
        assert result.status == "partially_refunded"


class TestProcessRefundErrors:
    """Testes de cenários de erro."""

    @pytest.mark.asyncio
    async def test_payment_not_found(self, payment_repo, use_case):
        """Lança PaymentNotFoundException se pagamento não existir."""
        payment_repo.get_by_id.return_value = None

        dto = ProcessRefundDTO(payment_id=uuid4(), refund_percentage=100)

        with pytest.raises(PaymentNotFoundException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_payment_not_completed(self, payment_repo, use_case):
        """Lança RefundException se pagamento não estiver COMPLETED."""
        payment = _make_payment(status=PaymentStatus.PENDING)
        payment_repo.get_by_id.return_value = payment

        dto = ProcessRefundDTO(payment_id=payment.id, refund_percentage=100)

        with pytest.raises(RefundException, match="não pode ser reembolsado"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_payment_without_gateway_id(self, payment_repo, use_case):
        """Lança RefundException se Payment não tiver gateway_payment_id."""
        payment = _make_payment()
        payment.gateway_payment_id = None
        payment_repo.get_by_id.return_value = payment

        dto = ProcessRefundDTO(payment_id=payment.id, refund_percentage=100)

        with pytest.raises(RefundException, match="ID do gateway"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_instructor_without_mp_account(
        self, payment_repo, instructor_repo, use_case
    ):
        """Lança RefundException se instrutor não tiver conta MP."""
        payment = _make_payment()
        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile(has_mp=False)

        dto = ProcessRefundDTO(payment_id=payment.id, refund_percentage=100)

        with pytest.raises(RefundException, match="sem conta Mercado Pago"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_gateway_failure(
        self, payment_repo, instructor_repo, gateway, use_case
    ):
        """Lança RefundException se gateway falhar."""
        payment = _make_payment()
        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.side_effect = Exception("MP API timeout")

        dto = ProcessRefundDTO(payment_id=payment.id, refund_percentage=100)

        with patch(
            "src.application.use_cases.payment.process_refund.decrypt_token",
            return_value="decrypted_token",
        ):
            with pytest.raises(RefundException, match="Falha ao processar"):
                await use_case.execute(dto)
