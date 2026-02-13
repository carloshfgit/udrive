import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


class TestSchedulingCancellation:

    def test_refund_gte_48h(self):
        """Cancelamento >= 48h antes da aula: 100% reembolso."""
        future_date = datetime.now(timezone.utc) + timedelta(hours=49)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_between_24h_48h(self):
        """Cancelamento entre 24h e 48h antes da aula: 50% reembolso."""
        future_date = datetime.now(timezone.utc) + timedelta(hours=30)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 50

    def test_refund_lt_24h(self):
        """Cancelamento < 24h antes da aula: 0% reembolso."""
        future_date = datetime.now(timezone.utc) + timedelta(hours=12)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 0

    def test_refund_naive_datetime(self):
        """Funciona corretamente com datetime naive (assume UTC)."""
        # 3 dias à frente garante >= 48h mesmo com offset de timezone
        naive_future_date = datetime.now() + timedelta(days=3)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=naive_future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_with_original_datetime_trava(self):
        """Após reagendamento, usa original_scheduled_datetime para cálculo.

        Mesmo se a nova data é daqui a 3 dias (100%), a trava da data
        original (12h) deve retornar 0%.
        """
        new_date = datetime.now(timezone.utc) + timedelta(days=3)
        original_date = datetime.now(timezone.utc) + timedelta(hours=12)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=new_date,
            original_scheduled_datetime=original_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.CONFIRMED,
        )

        assert scheduling.calculate_refund_percentage() == 0

    def test_refund_exactly_48h(self):
        """Exatamente 48h antes: >= 48h, portanto 100%."""
        future_date = datetime.now(timezone.utc) + timedelta(hours=48, minutes=1)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 100

    def test_refund_exactly_24h(self):
        """Exatamente 24h antes: >= 24h, portanto 50%."""
        future_date = datetime.now(timezone.utc) + timedelta(hours=24, minutes=1)

        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING,
        )

        assert scheduling.calculate_refund_percentage() == 50

