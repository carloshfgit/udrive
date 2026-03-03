"""
Testes unitários para CancelSchedulingUseCase.

Usa mocks para repositórios e ProcessRefundUseCase para testar
a lógica de orquestração isoladamente.
"""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.application.dtos.payment_dtos import (
    CancelSchedulingDTO,
    RefundResultDTO,
)
from src.application.use_cases.payment.cancel_scheduling import (
    CancelSchedulingUseCase,
)
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    CancellationException,
    SchedulingNotFoundException,
)


@pytest.fixture
def student_id():
    return uuid4()


@pytest.fixture
def instructor_id():
    return uuid4()


@pytest.fixture
def scheduling_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def payment_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def process_refund_uc():
    return AsyncMock()


@pytest.fixture
def use_case(scheduling_repo, payment_repo, process_refund_uc):
    return CancelSchedulingUseCase(
        scheduling_repository=scheduling_repo,
        payment_repository=payment_repo,
        process_refund_use_case=process_refund_uc,
    )


def _make_scheduling(
    student_id,
    instructor_id,
    hours_ahead: int = 72,
    status: SchedulingStatus = SchedulingStatus.CONFIRMED,
) -> Scheduling:
    """Helper para criar Scheduling com data configurável."""
    return Scheduling(
        id=uuid4(),
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.now(timezone.utc) + timedelta(hours=hours_ahead),
        price=Decimal("100.00"),
        status=status,
    )


def _make_payment(scheduling_id, student_id, instructor_id) -> Payment:
    """Helper para criar Payment associado a um scheduling."""
    return Payment(
        scheduling_id=scheduling_id,
        student_id=student_id,
        instructor_id=instructor_id,
        amount=Decimal("100.00"),
        platform_fee_percentage=Decimal("20.00"),
        status=PaymentStatus.COMPLETED,
        gateway_payment_id="mp_payment_123",
    )


class TestCancelSchedulingSuccess:
    """Testes de cancelamento bem-sucedido."""

    @pytest.mark.asyncio
    async def test_cancel_with_100_refund(
        self, student_id, instructor_id, scheduling_repo, payment_repo, process_refund_uc, use_case
    ):
        """Cancelamento >= 48h → 100% reembolso, chama ProcessRefundUseCase."""
        scheduling = _make_scheduling(student_id, instructor_id, hours_ahead=72)
        payment = _make_payment(scheduling.id, student_id, instructor_id)

        scheduling_repo.get_by_id.return_value = scheduling
        payment_repo.get_by_scheduling_id.return_value = payment
        process_refund_uc.execute.return_value = RefundResultDTO(
            payment_id=payment.id,
            refund_amount=Decimal("100.00"),
            refund_percentage=100,
            status="refunded",
            refunded_at=datetime.now(timezone.utc),
        )

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
            reason="Não posso ir",
        )
        result = await use_case.execute(dto)

        assert result.status == "cancelled"
        assert result.refund_percentage == 100
        assert result.refund_amount == Decimal("100.00")
        scheduling_repo.update.assert_called_once()
        process_refund_uc.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_with_50_refund(
        self, student_id, instructor_id, scheduling_repo, payment_repo, process_refund_uc, use_case
    ):
        """Cancelamento 24-48h → 50% reembolso."""
        scheduling = _make_scheduling(student_id, instructor_id, hours_ahead=36)
        payment = _make_payment(scheduling.id, student_id, instructor_id)

        scheduling_repo.get_by_id.return_value = scheduling
        payment_repo.get_by_scheduling_id.return_value = payment
        process_refund_uc.execute.return_value = RefundResultDTO(
            payment_id=payment.id,
            refund_amount=Decimal("50.00"),
            refund_percentage=50,
            status="partially_refunded",
            refunded_at=datetime.now(timezone.utc),
        )

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )
        result = await use_case.execute(dto)

        assert result.refund_percentage == 50
        assert result.refund_amount == Decimal("50.00")
        process_refund_uc.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_with_0_refund_no_gateway_call(
        self, student_id, instructor_id, scheduling_repo, payment_repo, process_refund_uc, use_case
    ):
        """Cancelamento < 24h → 0% reembolso, NÃO chama gateway."""
        scheduling = _make_scheduling(student_id, instructor_id, hours_ahead=12)

        scheduling_repo.get_by_id.return_value = scheduling

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )
        result = await use_case.execute(dto)

        assert result.refund_percentage == 0
        assert result.refund_amount is None
        assert result.refund_status is None
        process_refund_uc.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_instructor_cancels_always_100(
        self, student_id, instructor_id, scheduling_repo, payment_repo, process_refund_uc, use_case
    ):
        """Instrutor cancela < 24h → ainda 100% reembolso."""
        scheduling = _make_scheduling(student_id, instructor_id, hours_ahead=6)
        payment = _make_payment(scheduling.id, student_id, instructor_id)

        scheduling_repo.get_by_id.return_value = scheduling
        payment_repo.get_by_scheduling_id.return_value = payment
        process_refund_uc.execute.return_value = RefundResultDTO(
            payment_id=payment.id,
            refund_amount=Decimal("100.00"),
            refund_percentage=100,
            status="refunded",
            refunded_at=datetime.now(timezone.utc),
        )

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=instructor_id,  # INSTRUTOR cancela
        )
        result = await use_case.execute(dto)

        assert result.refund_percentage == 100
        assert result.refund_amount == Decimal("100.00")
        process_refund_uc.execute.assert_called_once()


class TestCancelSchedulingErrors:
    """Testes de cenários de erro."""

    @pytest.mark.asyncio
    async def test_scheduling_not_found(self, scheduling_repo, use_case):
        """Lança SchedulingNotFoundException se não encontrar."""
        scheduling_repo.get_by_id.return_value = None

        dto = CancelSchedulingDTO(
            scheduling_id=uuid4(),
            cancelled_by=uuid4(),
        )

        with pytest.raises(SchedulingNotFoundException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_scheduling_already_cancelled(
        self, student_id, instructor_id, scheduling_repo, use_case
    ):
        """Lança CancellationException se já estiver cancelado."""
        scheduling = _make_scheduling(
            student_id, instructor_id, status=SchedulingStatus.CANCELLED
        )
        scheduling_repo.get_by_id.return_value = scheduling

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )

        with pytest.raises(CancellationException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_scheduling_completed_cannot_cancel(
        self, student_id, instructor_id, scheduling_repo, use_case
    ):
        """Lança CancellationException se aula já concluída."""
        scheduling = _make_scheduling(
            student_id, instructor_id, status=SchedulingStatus.COMPLETED
        )
        scheduling_repo.get_by_id.return_value = scheduling

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )

        with pytest.raises(CancellationException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_no_payment_found_skips_refund(
        self, student_id, instructor_id, scheduling_repo, payment_repo, process_refund_uc, use_case
    ):
        """Se não houver Payment associado, cancela sem reembolso."""
        scheduling = _make_scheduling(student_id, instructor_id, hours_ahead=72)

        scheduling_repo.get_by_id.return_value = scheduling
        payment_repo.get_by_scheduling_id.return_value = None  # Sem pagamento

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )
        result = await use_case.execute(dto)

        assert result.status == "cancelled"
        assert result.refund_percentage == 100  # Calculou mas não executou
        assert result.refund_amount is None
        process_refund_uc.execute.assert_not_called()
