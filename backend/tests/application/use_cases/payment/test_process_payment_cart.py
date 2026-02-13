from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.dtos.payment_dtos import ProcessPaymentDTO, StudentPriceDTO
from src.application.use_cases.payment.process_payment import ProcessPaymentUseCase
from src.domain.entities.payment import PaymentStatus
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import SchedulingNotFoundException


class TestProcessPaymentCart:
    """Testes para checkout de carrinho (múltiplos agendamentos)."""

    @pytest.fixture
    def mock_repos(self):
        return {
            "scheduling": AsyncMock(),
            "payment": AsyncMock(),
            "transaction": AsyncMock(),
            "instructor": AsyncMock(),
            "user": AsyncMock(),
            "gateway": AsyncMock(),
            "calc_split": MagicMock(),
            "calc_price": MagicMock(),
        }

    @pytest.fixture
    def use_case(self, mock_repos):
        return ProcessPaymentUseCase(
            scheduling_repository=mock_repos["scheduling"],
            payment_repository=mock_repos["payment"],
            transaction_repository=mock_repos["transaction"],
            instructor_repository=mock_repos["instructor"],
            user_repository=mock_repos["user"],
            payment_gateway=mock_repos["gateway"],
            calculate_split_use_case=mock_repos["calc_split"],
            calculate_student_price_use_case=mock_repos["calc_price"],
        )

    @pytest.mark.asyncio
    async def test_checkout_multiple_schedulings_success(self, use_case, mock_repos):
        """Deve processar checkout de múltiplos agendamentos com sucesso."""
        student_id = uuid4()
        instructor_id = uuid4()
        s1_id = uuid4()
        s2_id = uuid4()

        # Mock agendamentos
        s1 = MagicMock(id=s1_id, instructor_id=instructor_id, price=Decimal("100.00"), status=SchedulingStatus.PENDING)
        s2 = MagicMock(id=s2_id, instructor_id=instructor_id, price=Decimal("150.00"), status=SchedulingStatus.PENDING)
        mock_repos["scheduling"].get_by_id.side_effect = [s1, s2]

        # Mock no existing payment
        mock_repos["payment"].get_by_scheduling_id.return_value = None

        # Mock instructor profile
        mock_repos["instructor"].get_by_user_id.return_value = MagicMock(stripe_account_id="acct_123")

        # Mock price calculation
        mock_repos["calc_price"].execute.side_effect = [
            StudentPriceDTO(instructor_amount=Decimal("100.00"), platform_fee_amount=Decimal("20.00"), 
                            stripe_fee_estimate=Decimal("5.00"), total_student_price=Decimal("125.00"), payment_method="card"),
            StudentPriceDTO(instructor_amount=Decimal("150.00"), platform_fee_amount=Decimal("30.00"), 
                            stripe_fee_estimate=Decimal("7.50"), total_student_price=Decimal("187.50"), payment_method="card"),
        ]

        # Mock Gateway PaymentIntent
        mock_repos["gateway"].create_payment_intent.return_value = MagicMock(
            payment_intent_id="pi_abc", client_secret="secret_123"
        )
        
        # Mock payment creation to return a saved payment
        def create_payment_mock(p):
            p.id = uuid4()
            p.created_at = datetime.now()
            return p
        mock_repos["payment"].create.side_effect = create_payment_mock

        # Execute
        dto = ProcessPaymentDTO(scheduling_ids=[s1_id, s2_id], student_id=student_id)
        result = await use_case.execute(dto)

        # Assertions
        assert len(result.payments) == 2
        assert result.total_amount == Decimal("125.00") + Decimal("187.50")
        assert result.client_secret == "secret_123"
        assert result.transfer_group.startswith("cart_")

        # Verificar se chamou gateway com o total correto
        mock_repos["gateway"].create_payment_intent.assert_called_once()
        call_args = mock_repos["gateway"].create_payment_intent.call_args[1]
        assert call_args["amount"] == result.total_amount
        assert call_args["transfer_group"] == result.transfer_group

        # Verificar se criou 2 payments e 2 transactions
        assert mock_repos["payment"].create.call_count == 2
        assert mock_repos["transaction"].create.call_count == 2

    @pytest.mark.asyncio
    async def test_checkout_fails_if_one_scheduling_not_found(self, use_case, mock_repos):
        """Deve falhar se um dos agendamentos no carrinho não for encontrado."""
        s1_id = uuid4()
        s2_id = uuid4()
        mock_repos["scheduling"].get_by_id.side_effect = [MagicMock(), None]

        dto = ProcessPaymentDTO(scheduling_ids=[s1_id, s2_id], student_id=uuid4())
        
        with pytest.raises(SchedulingNotFoundException):
            await use_case.execute(dto)

from datetime import datetime
