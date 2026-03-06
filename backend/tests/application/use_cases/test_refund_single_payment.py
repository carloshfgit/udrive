"""
Testes unitários para RefundSinglePaymentUseCase.

Cobre: sucesso (total e parcial), idempotência (mp_refund_id já existe),
validações de status, gateway_payment_id, instrutor sem conta MP,
falha no gateway, e scheduling não encontrado.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.application.dtos.payment_dtos import RefundSinglePaymentDTO
from src.application.use_cases.payment.refund_single_payment import (
    RefundSinglePaymentUseCase,
)
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    PaymentNotFoundException,
    RefundException,
    SchedulingNotFoundException,
)
from src.domain.interfaces.payment_gateway import RefundResult


# === Fixtures ===


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
def scheduling_repo():
    return AsyncMock()


@pytest.fixture
def gateway():
    return AsyncMock()


@pytest.fixture
def use_case(payment_repo, transaction_repo, instructor_repo, scheduling_repo, gateway):
    return RefundSinglePaymentUseCase(
        payment_repository=payment_repo,
        transaction_repository=transaction_repo,
        instructor_repository=instructor_repo,
        scheduling_repository=scheduling_repo,
        payment_gateway=gateway,
    )


# === Helpers ===


def _make_payment(
    amount: Decimal = Decimal("100.00"),
    status: PaymentStatus = PaymentStatus.COMPLETED,
    mp_refund_id: str | None = None,
    gateway_payment_id: str = "mp_pay_123",
) -> Payment:
    return Payment(
        scheduling_id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        amount=amount,
        platform_fee_percentage=Decimal("20.00"),
        status=status,
        gateway_payment_id=gateway_payment_id,
        mp_refund_id=mp_refund_id,
    )


def _make_instructor_profile(has_mp: bool = True):
    profile = MagicMock()
    profile.has_mp_account = has_mp
    profile.mp_access_token = "encrypted_token"
    return profile


def _make_scheduling(status: SchedulingStatus = SchedulingStatus.CONFIRMED):
    scheduling = MagicMock()
    scheduling.id = uuid4()
    scheduling.status = status
    scheduling.can_cancel = MagicMock(return_value=status in (
        SchedulingStatus.PENDING,
        SchedulingStatus.CONFIRMED,
        SchedulingStatus.RESCHEDULE_REQUESTED,
    ))
    scheduling.is_disputed = (status == SchedulingStatus.DISPUTED)

    # side_effects para simular mudança de status nos mocks
    def _cancel_side_effect(**kwargs):
        scheduling.status = SchedulingStatus.CANCELLED

    def _resolve_favor_student_side_effect():
        scheduling.status = SchedulingStatus.CANCELLED

    scheduling.cancel.side_effect = _cancel_side_effect
    scheduling.resolve_dispute_favor_student.side_effect = _resolve_favor_student_side_effect
    return scheduling


# === Testes de Sucesso ===


class TestRefundSinglePaymentSuccess:
    """Cenários de reembolso seletivo bem-sucedido."""

    @pytest.mark.asyncio
    async def test_full_refund_success(
        self, payment_repo, transaction_repo, instructor_repo, scheduling_repo, gateway, use_case
    ):
        """Reembolso total (100%): grava mp_refund_id, cria Transaction, cancela Scheduling."""
        payment = _make_payment()
        scheduling = _make_scheduling()
        admin_id = uuid4()

        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="mp_refund_001",
            amount=Decimal("100.00"),
            status="approved",
        )
        scheduling_repo.get_by_id.return_value = scheduling

        dto = RefundSinglePaymentDTO(
            payment_id=payment.id,
            admin_id=admin_id,
            refund_percentage=100,
            reason="Disputa resolvida a favor do aluno",
        )

        with patch(
            "src.application.use_cases.payment.refund_single_payment.decrypt_token",
            return_value="decrypted_token",
        ):
            result = await use_case.execute(dto)

        # Verifica resultado
        assert result.mp_refund_id == "mp_refund_001"
        assert result.refund_amount == Decimal("100.00")
        assert result.payment_status == "refunded"
        assert result.scheduling_status == SchedulingStatus.CANCELLED.value

        # Verifica que mp_refund_id foi gravado no Payment
        assert payment.mp_refund_id == "mp_refund_001"
        assert payment.status == PaymentStatus.REFUNDED

        # Verifica persistência
        payment_repo.update.assert_called_once_with(payment)
        transaction_repo.create.assert_called_once()
        scheduling.cancel.assert_called_once_with(
            cancelled_by=admin_id, reason="Disputa resolvida a favor do aluno"
        )
        scheduling_repo.update.assert_called_once_with(scheduling)

    @pytest.mark.asyncio
    async def test_partial_refund_50_percent(
        self, payment_repo, transaction_repo, instructor_repo, scheduling_repo, gateway, use_case
    ):
        """Reembolso parcial (50%): calcula valor correto, status PARTIALLY_REFUNDED."""
        payment = _make_payment(amount=Decimal("200.00"))
        scheduling = _make_scheduling()

        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="mp_refund_002",
            amount=Decimal("100.00"),
            status="approved",
        )
        scheduling_repo.get_by_id.return_value = scheduling

        dto = RefundSinglePaymentDTO(
            payment_id=payment.id,
            admin_id=uuid4(),
            refund_percentage=50,
        )

        with patch(
            "src.application.use_cases.payment.refund_single_payment.decrypt_token",
            return_value="decrypted_token",
        ):
            result = await use_case.execute(dto)

        assert result.refund_amount == Decimal("100.00")
        assert result.payment_status == "partially_refunded"
        assert payment.mp_refund_id == "mp_refund_002"

    @pytest.mark.asyncio
    async def test_scheduling_in_dispute_resolves_favor_student(
        self, payment_repo, transaction_repo, instructor_repo, scheduling_repo, gateway, use_case
    ):
        """Se Scheduling está em DISPUTED, resolve a favor do aluno ao invés de cancel()."""
        payment = _make_payment()
        scheduling = _make_scheduling(status=SchedulingStatus.DISPUTED)

        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="mp_refund_003",
            amount=Decimal("100.00"),
            status="approved",
        )
        scheduling_repo.get_by_id.return_value = scheduling

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

        with patch(
            "src.application.use_cases.payment.refund_single_payment.decrypt_token",
            return_value="decrypted_token",
        ):
            result = await use_case.execute(dto)

        scheduling.resolve_dispute_favor_student.assert_called_once()
        scheduling.cancel.assert_not_called()


# === Testes de Erro ===


class TestRefundSinglePaymentErrors:
    """Cenários de validação e erro."""

    @pytest.mark.asyncio
    async def test_payment_not_found(self, payment_repo, use_case):
        """Lança PaymentNotFoundException se pagamento não existir."""
        payment_repo.get_by_id.return_value = None

        dto = RefundSinglePaymentDTO(payment_id=uuid4(), admin_id=uuid4())

        with pytest.raises(PaymentNotFoundException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_payment_not_completed(self, payment_repo, use_case):
        """Lança RefundException se pagamento não estiver COMPLETED."""
        payment = _make_payment(status=PaymentStatus.PENDING)
        payment_repo.get_by_id.return_value = payment

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

        with pytest.raises(RefundException, match="não pode ser reembolsado"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_payment_already_refunded_idempotency(self, payment_repo, use_case):
        """Lança RefundException se Payment já possui mp_refund_id (idempotência)."""
        payment = _make_payment(mp_refund_id="existing_refund_123")
        payment_repo.get_by_id.return_value = payment

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

        with pytest.raises(RefundException, match="já possui reembolso vinculado"):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_payment_without_gateway_id(self, payment_repo, use_case):
        """Lança RefundException se Payment não tiver gateway_payment_id."""
        payment = _make_payment(gateway_payment_id=None)
        payment_repo.get_by_id.return_value = payment

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

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

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

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

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

        with patch(
            "src.application.use_cases.payment.refund_single_payment.decrypt_token",
            return_value="decrypted_token",
        ):
            with pytest.raises(RefundException, match="Falha ao processar"):
                await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_scheduling_not_found(
        self, payment_repo, instructor_repo, scheduling_repo, gateway, use_case
    ):
        """Lança SchedulingNotFoundException se scheduling não existir."""
        payment = _make_payment()
        payment_repo.get_by_id.return_value = payment
        instructor_repo.get_by_user_id.return_value = _make_instructor_profile()
        gateway.process_refund.return_value = RefundResult(
            refund_id="mp_refund_004",
            amount=Decimal("100.00"),
            status="approved",
        )
        scheduling_repo.get_by_id.return_value = None

        dto = RefundSinglePaymentDTO(payment_id=payment.id, admin_id=uuid4())

        with patch(
            "src.application.use_cases.payment.refund_single_payment.decrypt_token",
            return_value="decrypted_token",
        ):
            with pytest.raises(SchedulingNotFoundException):
                await use_case.execute(dto)
