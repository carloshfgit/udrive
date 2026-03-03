"""
Testes para auto_complete() e open_dispute() na entidade Scheduling.
"""

import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


def _make_scheduling(**overrides) -> Scheduling:
    """Helper para criar um Scheduling com valores padrão."""
    defaults = dict(
        student_id=uuid4(),
        instructor_id=uuid4(),
        scheduled_datetime=datetime.now(timezone.utc) - timedelta(hours=48),
        price=Decimal("100.00"),
        duration_minutes=50,
        status=SchedulingStatus.CONFIRMED,
    )
    defaults.update(overrides)
    return Scheduling(**defaults)


# === auto_complete ===

class TestAutoComplete:
    def test_auto_complete_confirmed_lesson(self):
        scheduling = _make_scheduling()
        assert scheduling.status == SchedulingStatus.CONFIRMED

        scheduling.auto_complete()

        assert scheduling.status == SchedulingStatus.COMPLETED
        assert scheduling.completed_at is not None

    def test_auto_complete_without_started_at(self):
        """auto_complete deve funcionar mesmo sem started_at."""
        scheduling = _make_scheduling(started_at=None)

        scheduling.auto_complete()

        assert scheduling.status == SchedulingStatus.COMPLETED
        assert scheduling.started_at is None  # não altera started_at

    def test_auto_complete_without_student_confirmed_at(self):
        """auto_complete deve funcionar mesmo sem student_confirmed_at."""
        scheduling = _make_scheduling(student_confirmed_at=None)

        scheduling.auto_complete()

        assert scheduling.status == SchedulingStatus.COMPLETED
        assert scheduling.student_confirmed_at is None

    def test_auto_complete_rejected_for_pending(self):
        scheduling = _make_scheduling(status=SchedulingStatus.PENDING)

        with pytest.raises(ValueError, match="Auto-complete"):
            scheduling.auto_complete()

    def test_auto_complete_rejected_for_cancelled(self):
        scheduling = _make_scheduling(status=SchedulingStatus.CANCELLED)

        with pytest.raises(ValueError, match="Auto-complete"):
            scheduling.auto_complete()

    def test_auto_complete_rejected_for_completed(self):
        scheduling = _make_scheduling(status=SchedulingStatus.COMPLETED)

        with pytest.raises(ValueError, match="Auto-complete"):
            scheduling.auto_complete()

    def test_auto_complete_rejected_for_disputed(self):
        scheduling = _make_scheduling(status=SchedulingStatus.DISPUTED)

        with pytest.raises(ValueError, match="Auto-complete"):
            scheduling.auto_complete()


# === open_dispute ===

class TestOpenDispute:
    def test_open_dispute_after_lesson_ended(self):
        # Aula terminou 2h atrás
        scheduling = _make_scheduling(
            scheduled_datetime=datetime.now(timezone.utc) - timedelta(hours=3),
            duration_minutes=50,
        )
        assert scheduling.status == SchedulingStatus.CONFIRMED

        scheduling.open_dispute()

        assert scheduling.status == SchedulingStatus.DISPUTED

    def test_open_dispute_rejected_before_lesson_ends(self):
        # Aula ainda nem começou
        scheduling = _make_scheduling(
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(hours=2),
        )

        with pytest.raises(ValueError, match="após o término"):
            scheduling.open_dispute()

    def test_open_dispute_rejected_for_pending(self):
        scheduling = _make_scheduling(
            status=SchedulingStatus.PENDING,
            scheduled_datetime=datetime.now(timezone.utc) - timedelta(hours=3),
        )

        with pytest.raises(ValueError, match="confirmadas"):
            scheduling.open_dispute()

    def test_open_dispute_rejected_for_completed(self):
        scheduling = _make_scheduling(
            status=SchedulingStatus.COMPLETED,
            scheduled_datetime=datetime.now(timezone.utc) - timedelta(hours=3),
        )

        with pytest.raises(ValueError, match="confirmadas"):
            scheduling.open_dispute()

    def test_is_disputed_property(self):
        scheduling = _make_scheduling(status=SchedulingStatus.DISPUTED)
        assert scheduling.is_disputed is True

        scheduling2 = _make_scheduling(status=SchedulingStatus.CONFIRMED)
        assert scheduling2.is_disputed is False
