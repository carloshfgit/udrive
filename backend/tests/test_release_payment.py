"""
Tests for ReleasePaymentUseCase

Testes unitários para o caso de uso de liberação de pagamento
retido em custódia (escrow) para o instrutor.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.use_cases.payment.release_payment import ReleasePaymentUseCase
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.exceptions import (
    PaymentNotFoundException,
    PaymentNotHeldException,
    StripeAccountNotConnectedException,
)
from src.domain.interfaces.payment_gateway import TransferResult


# =============================================================================
# Fixtures
# =============================================================================


def make_held_payment(**kwargs) -> Payment:
    """Cria um Payment em estado HELD para testes."""
    payment = Payment(
        scheduling_id=kwargs.get("scheduling_id", uuid4()),
        student_id=kwargs.get("student_id", uuid4()),
        instructor_id=kwargs.get("instructor_id", uuid4()),
        amount=Decimal("100.00"),
    )
    payment.mark_processing("pi_test_123")
    payment.mark_held()
    payment.transfer_group = f"payment_{payment.id}"
    return payment


def make_instructor_profile(user_id, stripe_account_id="acct_test_123"):
    """Cria mock de perfil de instrutor."""
    profile = MagicMock()
    profile.user_id = user_id
    profile.stripe_account_id = stripe_account_id
    return profile


def make_use_case(
    payment=None,
    instructor_profile=None,
    transfer_result=None,
):
    """Cria o ReleasePaymentUseCase com mocks configurados."""
    payment_repo = AsyncMock()
    transaction_repo = AsyncMock()
    payment_gateway = AsyncMock()
    instructor_repo = AsyncMock()

    if payment is not None:
        payment_repo.get_by_scheduling_id.return_value = payment
    else:
        payment_repo.get_by_scheduling_id.return_value = None

    if instructor_profile is not None:
        instructor_repo.get_by_user_id.return_value = instructor_profile
    else:
        instructor_repo.get_by_user_id.return_value = None

    if transfer_result is not None:
        payment_gateway.create_transfer.return_value = transfer_result
    else:
        payment_gateway.create_transfer.return_value = TransferResult(
            transfer_id="tr_test_456",
            amount=Decimal("80.00"),
            status="transfer",
            destination="acct_test_123",
        )

    uc = ReleasePaymentUseCase(
        payment_repository=payment_repo,
        transaction_repository=transaction_repo,
        payment_gateway=payment_gateway,
        instructor_repository=instructor_repo,
    )

    return uc, payment_repo, transaction_repo, payment_gateway, instructor_repo


# =============================================================================
# Testes
# =============================================================================


class TestReleasePaymentHappyPath:
    @pytest.mark.asyncio
    async def test_release_payment_success(self):
        """Fluxo completo: busca payment HELD, transfer, marca COMPLETED."""
        scheduling_id = uuid4()
        payment = make_held_payment(scheduling_id=scheduling_id)
        instructor_profile = make_instructor_profile(payment.instructor_id)

        uc, payment_repo, transaction_repo, payment_gateway, _ = make_use_case(
            payment=payment,
            instructor_profile=instructor_profile,
        )

        await uc.execute(scheduling_id)

        # Verificações
        payment_repo.get_by_scheduling_id.assert_called_once_with(scheduling_id)
        payment_gateway.create_transfer.assert_called_once()
        payment_repo.update.assert_called_once()
        transaction_repo.create.assert_called_once()

        # Payment deve estar COMPLETED
        updated_payment = payment_repo.update.call_args[0][0]
        assert updated_payment.status == PaymentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_transfer_uses_correct_amount(self):
        """Verifica que o transfer usa o instructor_amount, não o total."""
        payment = make_held_payment()
        instructor_profile = make_instructor_profile(payment.instructor_id, "acct_instr_789")

        uc, _, _, payment_gateway, _ = make_use_case(
            payment=payment,
            instructor_profile=instructor_profile,
        )

        await uc.execute(payment.scheduling_id)

        call_kwargs = payment_gateway.create_transfer.call_args
        assert call_kwargs[1]["amount"] == payment.instructor_amount
        assert call_kwargs[1]["destination_account_id"] == "acct_instr_789"
        assert call_kwargs[1]["transfer_group"] == payment.transfer_group


class TestReleasePaymentErrors:
    @pytest.mark.asyncio
    async def test_payment_not_found_raises(self):
        uc, _, _, _, _ = make_use_case(payment=None)

        with pytest.raises(PaymentNotFoundException):
            await uc.execute(uuid4())

    @pytest.mark.asyncio
    async def test_payment_not_held_raises(self):
        """Payment em PROCESSING (não HELD) deve lançar exceção."""
        payment = Payment(
            scheduling_id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            amount=Decimal("100.00"),
        )
        payment.mark_processing("pi_test_123")
        # Não chama mark_held() → status = PROCESSING

        uc, _, _, _, _ = make_use_case(payment=payment)

        with pytest.raises(PaymentNotHeldException):
            await uc.execute(payment.scheduling_id)

    @pytest.mark.asyncio
    async def test_instructor_without_stripe_raises(self):
        payment = make_held_payment()
        instructor_profile = make_instructor_profile(
            payment.instructor_id, stripe_account_id=None
        )

        uc, _, _, _, _ = make_use_case(
            payment=payment,
            instructor_profile=instructor_profile,
        )

        with pytest.raises(StripeAccountNotConnectedException):
            await uc.execute(payment.scheduling_id)

    @pytest.mark.asyncio
    async def test_instructor_profile_not_found_raises(self):
        payment = make_held_payment()

        uc, _, _, _, _ = make_use_case(
            payment=payment,
            instructor_profile=None,
        )

        with pytest.raises(StripeAccountNotConnectedException):
            await uc.execute(payment.scheduling_id)
