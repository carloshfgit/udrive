from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus

def create_base_scheduling():
    return Scheduling(
        id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=1),
        duration_minutes=60,
        price=100.0,
        status=SchedulingStatus.CONFIRMED,
        created_at=datetime.now(timezone.utc),
    )

def test_student_requests_reschedule():
    scheduling = create_base_scheduling()
    new_date = datetime.now(timezone.utc) + timedelta(days=2)
    requester_id = scheduling.student_id
    
    scheduling.request_reschedule(new_date, requester_id)
    
    assert scheduling.status == SchedulingStatus.RESCHEDULE_REQUESTED
    assert scheduling.rescheduled_datetime == new_date
    assert scheduling.rescheduled_by == requester_id

def test_instructor_requests_reschedule():
    scheduling = create_base_scheduling()
    new_date = datetime.now(timezone.utc) + timedelta(days=2)
    requester_id = scheduling.instructor_id
    
    scheduling.request_reschedule(new_date, requester_id)
    
    assert scheduling.status == SchedulingStatus.RESCHEDULE_REQUESTED
    assert scheduling.rescheduled_datetime == new_date
    assert scheduling.rescheduled_by == requester_id

def test_accept_student_reschedule_by_instructor():
    scheduling = create_base_scheduling()
    new_date = datetime.now(timezone.utc) + timedelta(days=2)
    scheduling.request_reschedule(new_date, scheduling.student_id)
    
    scheduling.accept_reschedule()
    
    assert scheduling.status == SchedulingStatus.CONFIRMED
    assert scheduling.scheduled_datetime == new_date
    assert scheduling.rescheduled_datetime is None
    assert scheduling.rescheduled_by is None

def test_refuse_instructor_reschedule_by_student():
    scheduling = create_base_scheduling()
    new_date = datetime.now(timezone.utc) + timedelta(days=2)
    scheduling.request_reschedule(new_date, scheduling.instructor_id)
    
    scheduling.refuse_reschedule()
    
    assert scheduling.status == SchedulingStatus.CONFIRMED
    assert scheduling.rescheduled_datetime is None
    assert scheduling.rescheduled_by is None
