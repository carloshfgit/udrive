import pytest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus

class TestSchedulingCancellation:
    
    def test_calculate_refund_percentage_naive_datetime(self):
        """test_calculate_refund_percentage_naive_datetime
        
        Testa se o cálculo de reembolso funciona mesmo quando a data do agendamento 
        é 'naive' (sem timezone definido).
        """
        # Arrange
        # Data futura (naive)
        naive_future_date = datetime.now() + timedelta(days=2)
        
        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=naive_future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING
        )
        
        # Act
        refund_pct = scheduling.calculate_refund_percentage()
        
        # Assert
        # Como é > 24h, deve ser 100% de reembolso
        assert refund_pct == 100

    def test_calculate_refund_percentage_aware_datetime(self):
        """test_calculate_refund_percentage_aware_datetime
        
        Testa o cálculo com data contendo timezone (happy path).
        """
        # Arrange
        aware_future_date = datetime.now(timezone.utc) + timedelta(days=2)
        
        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=aware_future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING
        )
        
        # Act
        refund_pct = scheduling.calculate_refund_percentage()
        
        # Assert
        assert refund_pct == 100

    def test_calculate_refund_less_than_24h(self):
        """test_calculate_refund_less_than_24h
        
        Testa reembolso de 50% para cancelamento com menos de 24h.
        """
        # Arrange
        # 12 horas a partir de agora
        near_future_date = datetime.now(timezone.utc) + timedelta(hours=12)
        
        scheduling = Scheduling(
            id=uuid4(),
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=near_future_date,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING
        )
        
        # Act
        refund_pct = scheduling.calculate_refund_percentage()
        
        # Assert
        assert refund_pct == 50
