"""
Testes para schemas de agendamento e perfil — campos de pagamento.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.interface.api.schemas.scheduling_schemas import SchedulingResponse
from src.interface.api.schemas.profiles import InstructorProfileResponse


class TestSchedulingResponsePaymentStatus:
    """Testa o campo payment_status no SchedulingResponse."""

    def _base_data(self, **overrides):
        data = {
            "id": uuid4(),
            "student_id": uuid4(),
            "instructor_id": uuid4(),
            "scheduled_datetime": datetime(2026, 3, 1, 10, 0),
            "duration_minutes": 50,
            "price": Decimal("89.90"),
            "status": "confirmed",
            "created_at": datetime(2026, 2, 28, 12, 0),
        }
        data.update(overrides)
        return data

    def test_payment_status_default_none(self):
        """payment_status deve ser None por padrão."""
        resp = SchedulingResponse(**self._base_data())
        assert resp.payment_status is None

    def test_payment_status_completed(self):
        """payment_status aceita valor string."""
        resp = SchedulingResponse(**self._base_data(payment_status="COMPLETED"))
        assert resp.payment_status == "COMPLETED"

    def test_payment_status_pending(self):
        """payment_status aceita PENDING."""
        resp = SchedulingResponse(**self._base_data(payment_status="PENDING"))
        assert resp.payment_status == "PENDING"

    def test_payment_status_explicitly_none(self):
        """payment_status pode receber None explicitamente."""
        resp = SchedulingResponse(**self._base_data(payment_status=None))
        assert resp.payment_status is None


class TestInstructorProfileResponseHasMpAccount:
    """Testa o campo has_mp_account no InstructorProfileResponse."""

    def _base_data(self, **overrides):
        data = {
            "id": uuid4(),
            "user_id": uuid4(),
            "bio": "Instrutor experiente",
            "vehicle_type": "car",
            "license_category": "B",
            "hourly_rate": Decimal("80.00"),
            "rating": 4.8,
            "total_reviews": 25,
            "is_available": True,
        }
        data.update(overrides)
        return data

    def test_has_mp_account_default_false(self):
        """has_mp_account deve ser False por padrão."""
        resp = InstructorProfileResponse(**self._base_data())
        assert resp.has_mp_account is False

    def test_has_mp_account_true(self):
        """has_mp_account aceita True."""
        resp = InstructorProfileResponse(**self._base_data(has_mp_account=True))
        assert resp.has_mp_account is True

    def test_has_mp_account_false_explicit(self):
        """has_mp_account pode receber False explicitamente."""
        resp = InstructorProfileResponse(**self._base_data(has_mp_account=False))
        assert resp.has_mp_account is False
