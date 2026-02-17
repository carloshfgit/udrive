import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


class TestSchedulingCancellation:

    def _make_scheduling(self, scheduled_datetime: datetime) -> Scheduling:
        """Helper para criar Scheduling com data configurável."""
        return Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=scheduled_datetime,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

    # ===== Faixa 1: >= 48h → 100% =====

    def test_refund_100_percent_when_more_than_48h(self):
        """Reembolso integral quando >= 48h antes da aula."""
        dt = datetime.now(timezone.utc) + timedelta(hours=72)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_100_percent_at_exactly_48h(self):
        """Edge case: exatamente 48h → 100%."""
        dt = datetime.now(timezone.utc) + timedelta(hours=48, minutes=1)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 100

    # ===== Faixa 2: 24-48h → 50% =====

    def test_refund_50_percent_between_24_and_48h(self):
        """Reembolso de 50% quando entre 24h e 48h."""
        dt = datetime.now(timezone.utc) + timedelta(hours=36)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 50

    def test_refund_50_percent_at_exactly_24h(self):
        """Edge case: exatamente 24h → 50%."""
        dt = datetime.now(timezone.utc) + timedelta(hours=24, minutes=1)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 50

    # ===== Faixa 3: < 24h → 0% =====

    def test_refund_0_percent_less_than_24h(self):
        """Sem reembolso quando < 24h antes da aula."""
        dt = datetime.now(timezone.utc) + timedelta(hours=12)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 0

    def test_refund_0_percent_very_close(self):
        """Sem reembolso com apenas 1h de antecedência."""
        dt = datetime.now(timezone.utc) + timedelta(hours=1)
        scheduling = self._make_scheduling(dt)
        assert scheduling.calculate_refund_percentage() == 0

    # ===== Datetime naive =====

    def test_refund_with_naive_datetime_over_48h(self):
        """Testa cálculo com datetime naive (sem timezone) — >= 48h."""
        naive_dt = datetime.now() + timedelta(days=3)
        scheduling = self._make_scheduling(naive_dt)
        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_with_naive_datetime_under_24h(self):
        """Testa cálculo com datetime naive (sem timezone) — < 24h."""
        naive_dt = datetime.now() + timedelta(hours=12)
        scheduling = self._make_scheduling(naive_dt)
        assert scheduling.calculate_refund_percentage() == 0

    # ===== Cancelamento =====

    def test_can_cancel_pending(self):
        """Pode cancelar agendamento PENDING."""
        dt = datetime.now(timezone.utc) + timedelta(days=3)
        scheduling = self._make_scheduling(dt)
        assert scheduling.can_cancel() is True

    def test_can_cancel_confirmed(self):
        """Pode cancelar agendamento CONFIRMED."""
        dt = datetime.now(timezone.utc) + timedelta(days=3)
        scheduling = self._make_scheduling(dt)
        scheduling.status = SchedulingStatus.CONFIRMED
        assert scheduling.can_cancel() is True

    def test_cannot_cancel_completed(self):
        """Não pode cancelar agendamento COMPLETED."""
        dt = datetime.now(timezone.utc) + timedelta(days=3)
        scheduling = self._make_scheduling(dt)
        scheduling.status = SchedulingStatus.COMPLETED
        assert scheduling.can_cancel() is False

    def test_cancel_sets_status(self):
        """Cancel deve setar status para CANCELLED."""
        dt = datetime.now(timezone.utc) + timedelta(days=3)
        scheduling = self._make_scheduling(dt)
        user_id = uuid4()
        scheduling.cancel(cancelled_by=user_id, reason="Não posso ir")

        assert scheduling.status == SchedulingStatus.CANCELLED
        assert scheduling.cancelled_by == user_id
        assert scheduling.cancellation_reason == "Não posso ir"
        assert scheduling.cancelled_at is not None
