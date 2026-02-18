import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.application.use_cases.scheduling.respond_reschedule_use_case import RespondRescheduleUseCase
from src.application.dtos.scheduling_dtos import RespondRescheduleDTO
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.entities.user import User
from src.domain.entities.user_type import UserType
from src.domain.exceptions import UnavailableSlotException, SchedulingConflictException

@pytest.mark.asyncio
async def test_respond_reschedule_conflict():
    # Arrange
    scheduling_repo = AsyncMock()
    user_repo = AsyncMock()
    availability_repo = AsyncMock()
    
    use_case = RespondRescheduleUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
        availability_repository=availability_repo
    )
    
    scheduling_id = uuid4()
    instructor_id = uuid4()
    student_id = uuid4()
    new_datetime = datetime.now(timezone.utc) + timedelta(days=1)
    
    scheduling = MagicMock(spec=Scheduling)
    scheduling.id = scheduling_id
    scheduling.instructor_id = instructor_id
    scheduling.student_id = student_id
    scheduling.status = SchedulingStatus.RESCHEDULE_REQUESTED
    scheduling.rescheduled_datetime = new_datetime
    scheduling.duration_minutes = 50
    scheduling.rescheduled_by = student_id
    
    scheduling_repo.get_by_id.return_value = scheduling
    
    # Simulate conflict
    availability_repo.is_time_available.return_value = True
    scheduling_repo.check_conflict.return_value = True # CONFLICT!
    
    dto = RespondRescheduleDTO(
        scheduling_id=scheduling_id,
        user_id=instructor_id,
        accepted=True
    )
    
    # Act & Assert
    with pytest.raises(SchedulingConflictException) as exc:
        await use_case.execute(dto)
    
    assert "Ops! Outro aluno já agendou nesse horário" in str(exc.value)
    scheduling.accept_reschedule.assert_not_called()

@pytest.mark.asyncio
async def test_respond_reschedule_unavailable():
    # Arrange
    scheduling_repo = AsyncMock()
    user_repo = AsyncMock()
    availability_repo = AsyncMock()
    
    use_case = RespondRescheduleUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
        availability_repository=availability_repo
    )
    
    scheduling_id = uuid4()
    instructor_id = uuid4()
    student_id = uuid4()
    new_datetime = datetime.now(timezone.utc) + timedelta(days=1)
    
    scheduling = MagicMock(spec=Scheduling)
    scheduling.id = scheduling_id
    scheduling.instructor_id = instructor_id
    scheduling.student_id = student_id
    scheduling.status = SchedulingStatus.RESCHEDULE_REQUESTED
    scheduling.rescheduled_datetime = new_datetime
    scheduling.duration_minutes = 50
    scheduling.rescheduled_by = student_id
    
    scheduling_repo.get_by_id.return_value = scheduling
    
    # Simulate unavailability
    availability_repo.is_time_available.return_value = False # UNAVAILABLE!
    
    dto = RespondRescheduleDTO(
        scheduling_id=scheduling_id,
        user_id=instructor_id,
        accepted=True
    )
    
    # Act & Assert
    with pytest.raises(UnavailableSlotException) as exc:
        await use_case.execute(dto)
    
    assert "instrutor não tem mais disponibilidade" in str(exc.value)
    scheduling.accept_reschedule.assert_not_called()

@pytest.mark.asyncio
async def test_respond_reschedule_success():
    # Arrange
    scheduling_repo = AsyncMock()
    user_repo = AsyncMock()
    availability_repo = AsyncMock()
    
    use_case = RespondRescheduleUseCase(
        scheduling_repository=scheduling_repo,
        user_repository=user_repo,
        availability_repository=availability_repo
    )
    
    scheduling_id = uuid4()
    instructor_id = uuid4()
    student_id = uuid4()
    new_datetime = datetime.now(timezone.utc) + timedelta(days=1)
    
    scheduling = MagicMock(spec=Scheduling)
    scheduling.id = scheduling_id
    scheduling.instructor_id = instructor_id
    scheduling.student_id = student_id
    scheduling.student_name = "Student"
    scheduling.instructor_name = "Instructor"
    scheduling.status = SchedulingStatus.RESCHEDULE_REQUESTED
    scheduling.rescheduled_datetime = new_datetime
    scheduling.duration_minutes = 50
    scheduling.rescheduled_by = student_id
    scheduling.price = 100
    scheduling.created_at = datetime.now(timezone.utc)
    scheduling.scheduled_datetime = datetime.now(timezone.utc)
    
    scheduling_repo.get_by_id.return_value = scheduling
    scheduling_repo.update.return_value = scheduling
    
    student = User(id=student_id, email="s@test.com", hashed_password="hash", full_name="Student", user_type=UserType.STUDENT)
    instructor = User(id=instructor_id, email="i@test.com", hashed_password="hash", full_name="Instructor", user_type=UserType.INSTRUCTOR)
    
    user_repo.get_by_id.side_effect = lambda uid: student if uid == student_id else instructor
    
    # Simulate success
    availability_repo.is_time_available.return_value = True
    scheduling_repo.check_conflict.return_value = False
    
    dto = RespondRescheduleDTO(
        scheduling_id=scheduling_id,
        user_id=instructor_id,
        accepted=True
    )
    
    # Act
    await use_case.execute(dto)
    
    # Assert
    scheduling.accept_reschedule.assert_called_once()
    scheduling_repo.update.assert_called_once()
