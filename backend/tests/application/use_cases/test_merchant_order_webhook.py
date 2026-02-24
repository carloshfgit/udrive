
import pytest
from unittest.mock import AsyncMock, MagicMock, ANY
from uuid import uuid4
from decimal import Decimal

from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.application.use_cases.payment.handle_payment_webhook import HandlePaymentWebhookUseCase
from src.domain.entities.payment_status import PaymentStatus

@pytest.fixture(autouse=True)
def _bypass_decrypt(monkeypatch):
    """Bypass de criptografia: decrypt_token retorna o valor inalterado."""
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

@pytest.mark.asyncio
async def test_handle_merchant_order_webhook_success(mock_repositories, mock_gateway):
    """
    Testa se ao receber uma merchant_order, o use case busca a ordem
    e processa os pagamentos aprovados nela.
    """
    merchant_order_id = "MO123"
    payment_id_mp = "PAY456"
    group_id = uuid4()
    instructor_id = uuid4()

    # 1. Mock do Gateway para retornar a ordem
    mock_gateway.get_merchant_order.return_value = {
        "id": merchant_order_id,
        "external_reference": str(group_id),
        "payments": [
            {"id": payment_id_mp, "status": "approved"}
        ]
    }
    
    # Mock do Gateway para o status do pagamento individual
    from src.domain.interfaces.payment_gateway import PaymentStatusResult
    mock_gateway.get_payment_status.return_value = PaymentStatusResult(
        payment_id=payment_id_mp,
        status="approved",
        status_detail="accredited",
        payer_email="student@test.com"
    )

    # 2. Mock dos Repositórios
    payment = MagicMock()
    payment.id = uuid4()
    payment.instructor_id = instructor_id
    payment.student_id = uuid4()
    payment.amount = Decimal("100.00")
    payment.preference_group_id = group_id
    payment.status = PaymentStatus.PROCESSING
    payment.gateway_preference_id = "pref-123"
    payment.scheduling_id = uuid4()
    
    mock_repositories["payment"].get_by_gateway_payment_id.return_value = payment
    mock_repositories["payment"].get_by_preference_group_id.return_value = [payment]
    
    instructor = MagicMock()
    instructor.has_mp_account = True
    instructor.mp_access_token = "fake-token"
    mock_repositories["instructor"].get_by_mp_user_id.return_value = instructor

    scheduling = MagicMock()
    scheduling.id = payment.scheduling_id
    scheduling.can_confirm.return_value = True
    mock_repositories["scheduling"].get_by_id.return_value = scheduling
    
    # 3. Execução
    use_case = HandlePaymentWebhookUseCase(
        payment_repository=mock_repositories["payment"],
        scheduling_repository=mock_repositories["scheduling"],
        transaction_repository=mock_repositories["transaction"],
        instructor_repository=mock_repositories["instructor"],
        payment_gateway=mock_gateway
    )

    dto = WebhookNotificationDTO(
        notification_id=1,
        notification_type="merchant_order",
        action="",
        data_id=merchant_order_id,
        user_id="fake-mp-user-id"
    )

    await use_case.execute(dto)

    # 4. Verificações
    mock_gateway.get_merchant_order.assert_called_once_with(merchant_order_id, "fake-token")
    mock_gateway.get_payment_status.assert_called()
    mock_repositories["payment"].get_by_gateway_payment_id.assert_called_with(payment_id_mp)
    payment.mark_completed.assert_called_once()
    scheduling.confirm.assert_called_once()
