"""
Testes unitários para cancelamento e reembolso da entidade Scheduling.
"""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


class TestSchedulingCancellation:

    def _make_scheduling(
        self,
        scheduled_datetime: datetime,
        student_id=None,
        instructor_id=None,
    ) -> Scheduling:
        """Helper para criar Scheduling com data configurável."""
        return Scheduling(
            id=uuid4(),
            student_id=student_id or uuid4(),
            instructor_id=instructor_id or uuid4(),
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

    def test_can_cancel_reschedule_requested(self):
        """Pode cancelar agendamento com RESCHEDULE_REQUESTED."""
        dt = datetime.now(timezone.utc) + timedelta(days=3)
        scheduling = self._make_scheduling(dt)
        scheduling.status = SchedulingStatus.RESCHEDULE_REQUESTED
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


class TestRefundPercentageForCanceller:
    """Testes para calculate_refund_percentage_for_canceller."""

    def test_instructor_cancels_always_100(self):
        """Instrutor cancelando → sempre 100% reembolso, independente da antecedência."""
        instructor_id = uuid4()
        # Aula em 12h (normalmente 0%)
        dt = datetime.now(timezone.utc) + timedelta(hours=12)
        scheduling = Scheduling(
            student_id=uuid4(),
            instructor_id=instructor_id,
            scheduled_datetime=dt,
            price=Decimal("100.00"),
        )
        assert scheduling.calculate_refund_percentage_for_canceller(instructor_id) == 100

    def test_instructor_cancels_close_to_lesson(self):
        """Instrutor cancelando 1h antes → ainda 100%."""
        instructor_id = uuid4()
        dt = datetime.now(timezone.utc) + timedelta(hours=1)
        scheduling = Scheduling(
            student_id=uuid4(),
            instructor_id=instructor_id,
            scheduled_datetime=dt,
            price=Decimal("100.00"),
        )
        assert scheduling.calculate_refund_percentage_for_canceller(instructor_id) == 100

    def test_student_cancels_applies_standard_rules(self):
        """Aluno cancelando → aplica regras padrão de antecedência."""
        student_id = uuid4()
        # Aula em 36h → 50%
        dt = datetime.now(timezone.utc) + timedelta(hours=36)
        scheduling = Scheduling(
            student_id=student_id,
            instructor_id=uuid4(),
            scheduled_datetime=dt,
            price=Decimal("100.00"),
        )
        assert scheduling.calculate_refund_percentage_for_canceller(student_id) == 50

    def test_student_cancels_under_24h_gets_0(self):
        """Aluno cancelando < 24h → 0%."""
        student_id = uuid4()
        dt = datetime.now(timezone.utc) + timedelta(hours=12)
        scheduling = Scheduling(
            student_id=student_id,
            instructor_id=uuid4(),
            scheduled_datetime=dt,
            price=Decimal("100.00"),
        )
        assert scheduling.calculate_refund_percentage_for_canceller(student_id) == 0


class TestRescheduleRefundLock:
    """Testes para a trava de reembolso em reagendamentos dentro da janela de multa."""

    def test_reschedule_inside_penalty_preserves_original_date(self):
        """Reagendamento aceito < 48h do original preserva a data original."""
        student_id = uuid4()
        instructor_id = uuid4()
        # Aula original em 20h (dentro da janela de multa < 48h)
        original_dt = datetime.now(timezone.utc) + timedelta(hours=20)
        scheduling = Scheduling(
            student_id=student_id,
            instructor_id=instructor_id,
            scheduled_datetime=original_dt,
            price=Decimal("100.00"),
            status=SchedulingStatus.CONFIRMED,
        )

        # Solicita reagendamento para 7 dias no futuro
        new_dt = datetime.now(timezone.utc) + timedelta(days=7)
        scheduling.request_reschedule(new_datetime=new_dt, requester_id=student_id)
        scheduling.accept_reschedule()

        # Data original foi preservada
        assert scheduling.original_scheduled_datetime == original_dt
        # Data efetiva mudou
        assert scheduling.scheduled_datetime == new_dt
        # Reembolso usa data original (< 24h → 0%)
        assert scheduling.calculate_refund_percentage() == 0

    def test_reschedule_outside_penalty_no_lock(self):
        """Reagendamento aceito >= 48h do original NÃO preserva data."""
        student_id = uuid4()
        instructor_id = uuid4()
        # Aula original em 72h (fora da janela de multa)
        original_dt = datetime.now(timezone.utc) + timedelta(hours=72)
        scheduling = Scheduling(
            student_id=student_id,
            instructor_id=instructor_id,
            scheduled_datetime=original_dt,
            price=Decimal("100.00"),
            status=SchedulingStatus.CONFIRMED,
        )

        # Solicita reagendamento para 10 dias no futuro
        new_dt = datetime.now(timezone.utc) + timedelta(days=10)
        scheduling.request_reschedule(new_datetime=new_dt, requester_id=student_id)
        scheduling.accept_reschedule()

        # Data original NÃO foi preservada (sem trava)
        assert scheduling.original_scheduled_datetime is None
        # Data efetiva mudou
        assert scheduling.scheduled_datetime == new_dt
        # Reembolso usa data nova (> 48h → 100%)
        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_uses_original_when_locked(self):
        """Cálculo de reembolso usa data original quando trava está ativa."""
        scheduling = Scheduling(
            student_id=uuid4(),
            instructor_id=uuid4(),
            # Data efetiva está longe (reagendada para o futuro)
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=30),
            price=Decimal("100.00"),
            # Data original era 12h atrás da janela
            original_scheduled_datetime=datetime.now(timezone.utc) + timedelta(hours=12),
        )
        # Mesmo com a aula reagendada para 30 dias, usa os 12h originais → 0%
        assert scheduling.calculate_refund_percentage() == 0
