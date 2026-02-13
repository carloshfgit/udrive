import pytest
import unittest.mock
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus

def test_scheduling_reschedule_limit():
    """Testa o limite de 1 reagendamento."""
    student_id = uuid4()
    instructor_id = uuid4()
    original_time = datetime.now(timezone.utc) + timedelta(days=2)
    
    scheduling = Scheduling(
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=original_time,
        price=Decimal("100.00"),
        status=SchedulingStatus.PENDING
    )
    
    # 1. Primeiro pedido de reagendamento
    new_time_1 = original_time + timedelta(hours=2)
    scheduling.request_reschedule(new_time_1, student_id)
    scheduling.accept_reschedule()
    
    assert scheduling.reschedule_count == 1
    assert scheduling.scheduled_datetime == new_time_1
    assert scheduling.original_scheduled_datetime == original_time
    
    # 2. Segundo pedido deve ser bloqueado can_request_reschedule
    assert scheduling.can_request_reschedule() is False
    
    with pytest.raises(ValueError, match="Reagendamento não pode ser solicitado"):
        scheduling.request_reschedule(new_time_1 + timedelta(hours=1), student_id)

def test_scheduling_refund_lock_after_reschedule():
    """Testa se o reembolso usa a data original após reagendamento."""
    student_id = uuid4()
    instructor_id = uuid4()
    # Data original: daqui a 50 horas (100% reembolso)
    original_time = datetime.now(timezone.utc) + timedelta(hours=50)
    
    scheduling = Scheduling(
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=original_time,
        price=Decimal("100.00"),
        status=SchedulingStatus.PENDING
    )
    
    # Reagendar para daqui a 100 horas
    new_time = datetime.now(timezone.utc) + timedelta(hours=100)
    scheduling.request_reschedule(new_time, student_id)
    scheduling.accept_reschedule()
    
    # Agora estamos a menos de 48h da data ORIGINAL (50h - tempo passou um pouco)
    # Mas pela data NOVA (100h) seria 100%. 
    # Vamos simular que o tempo passou e agora faltam 40h para a ORIGINAL.
    
    # Simular que o tempo passou e agora faltam 40h para a ORIGINAL.
    with unittest.mock.patch('src.domain.entities.scheduling.datetime') as mock_dt:
        # Mock datetime.now(timezone.utc)
        mock_now = original_time - timedelta(hours=40)
        mock_dt.now.return_value = mock_now
        
        # calculate_refund_percentage usa datetime.now(timezone.utc)
        refund = scheduling.calculate_refund_percentage()
        assert refund == 50  # Deve travar na data original (40h < 48h)
