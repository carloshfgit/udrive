"""
Testes unitários para a Celery task de reembolso.

Usa mocks para validar que a task chama o ProcessRefundUseCase
corretamente e realiza retry em caso de falha.
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4


class TestProcessRefundTask:
    """Testes para a Celery task process_refund_task."""

    @patch("src.infrastructure.tasks.refund_tasks.asyncio")
    def test_success_returns_message(self, mock_asyncio):
        """Task retorna mensagem de sucesso com payment_id."""
        from src.infrastructure.tasks.refund_tasks import process_refund_task

        payment_id = str(uuid4())
        mock_asyncio.run.return_value = {
            "payment_id": payment_id,
            "refund_amount": "100.00",
            "status": "refunded",
        }

        result = process_refund_task.run(payment_id, 100, "Cancelamento")

        mock_asyncio.run.assert_called_once()
        assert payment_id in result

    @patch("src.infrastructure.tasks.refund_tasks.asyncio")
    def test_retry_on_failure(self, mock_asyncio):
        """Task faz retry em caso de exceção."""
        from src.infrastructure.tasks.refund_tasks import process_refund_task

        payment_id = str(uuid4())
        mock_asyncio.run.side_effect = Exception("MP API timeout")

        # bind=True faz com que self.retry() seja chamado.
        # Em modo de teste, precisamos verificar que a exceção é re-raised
        with pytest.raises(Exception):
            process_refund_task.run(payment_id, 100)

    @patch("src.infrastructure.tasks.refund_tasks.asyncio")
    def test_partial_refund_50(self, mock_asyncio):
        """Task funciona para reembolso parcial (50%)."""
        from src.infrastructure.tasks.refund_tasks import process_refund_task

        payment_id = str(uuid4())
        mock_asyncio.run.return_value = {
            "payment_id": payment_id,
            "refund_amount": "50.00",
            "status": "partially_refunded",
        }

        result = process_refund_task.run(payment_id, 50, None)

        assert payment_id in result

    @patch("src.infrastructure.tasks.refund_tasks.asyncio")
    def test_reason_is_optional(self, mock_asyncio):
        """Task aceita chamada sem reason (parâmetro opcional)."""
        from src.infrastructure.tasks.refund_tasks import process_refund_task

        payment_id = str(uuid4())
        mock_asyncio.run.return_value = {
            "payment_id": payment_id,
            "refund_amount": "100.00",
            "status": "refunded",
        }

        # Sem reason
        result = process_refund_task.run(payment_id, 100)

        assert payment_id in result
