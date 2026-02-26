
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from src.application.use_cases.scheduling.create_scheduling import CreateSchedulingUseCase
from src.application.dtos.scheduling_dtos import CreateSchedulingDTO
from src.domain.entities.user_type import UserType
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import MixedInstructorsException

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def mock_instructor_repo():
    return AsyncMock()

@pytest.fixture
def mock_scheduling_repo():
    return AsyncMock()

@pytest.fixture
def mock_availability_repo():
    return AsyncMock()

@pytest.fixture
def use_case(mock_user_repo, mock_instructor_repo, mock_scheduling_repo, mock_availability_repo):
    return CreateSchedulingUseCase(
        user_repository=mock_user_repo,
        instructor_repository=mock_instructor_repo,
        scheduling_repository=mock_scheduling_repo,
        availability_repository=mock_availability_repo
    )

@pytest.mark.asyncio
async def test_should_raise_error_when_cart_has_different_instructor(use_case, mock_scheduling_repo, mock_user_repo):
    # Arrange
    student_id = uuid4()
    target_instructor_id = uuid4()
    current_cart_instructor_id = uuid4() # Different instructor
    
    dto = CreateSchedulingDTO(
        student_id=student_id,
        instructor_id=target_instructor_id,
        scheduled_datetime=datetime.now(),
        lesson_category="B",
        vehicle_ownership="instructor",
        duration_minutes=60
    )

    # Mock student existence
    student = MagicMock()
    student.user_type = UserType.STUDENT
    student.is_active = True
    mock_user_repo.get_by_id.return_value = student

    # Mock cart containing item from DIFFERENT instructor
    cart_item = MagicMock(spec=Scheduling)
    cart_item.instructor_id = current_cart_instructor_id
    mock_scheduling_repo.list_by_student.return_value = [cart_item]

    # Act & Assert
    with pytest.raises(MixedInstructorsException) as exc:
        await use_case.execute(dto)
    
    assert "Você só pode agendar aulas com um instrutor por vez" in str(exc.value)
    mock_scheduling_repo.list_by_student.assert_called_with(
        student_id=student_id,
        payment_status_filter="pending",
        limit=1
    )

@pytest.mark.asyncio
async def test_should_succeed_when_cart_has_same_instructor(use_case, mock_scheduling_repo, mock_user_repo, mock_instructor_repo, mock_availability_repo):
    # Arrange
    student_id = uuid4()
    instructor_id = uuid4()
    
    dto = CreateSchedulingDTO(
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.now(),
        lesson_category="B",
        vehicle_ownership="instructor",
        duration_minutes=60
    )

    # Mock student
    student = MagicMock()
    student.user_type = UserType.STUDENT
    student.is_active = True
    student.full_name = "Student Name"
    mock_user_repo.get_by_id.side_effect = [student, MagicMock(full_name="Inst Name", user_type=UserType.INSTRUCTOR, is_active=True)]

    # Mock cart containing item from SAME instructor
    cart_item = MagicMock(spec=Scheduling)
    cart_item.instructor_id = instructor_id
    mock_scheduling_repo.list_by_student.return_value = [cart_item]

    # Mock other dependencies for success flow
    instructor_profile = MagicMock()
    instructor_profile.is_available = True
    instructor_profile.hourly_rate = 100
    instructor_profile.price_cat_b_instructor_vehicle = 100
    mock_instructor_repo.get_by_user_id.return_value = instructor_profile
    
    mock_availability_repo.is_time_available.return_value = True
    mock_scheduling_repo.check_conflict.return_value = False
    
    created_scheduling = MagicMock(spec=Scheduling)
    created_scheduling.id = uuid4()
    created_scheduling.student_id = student_id
    created_scheduling.instructor_id = instructor_id
    created_scheduling.status = SchedulingStatus.PENDING
    created_scheduling.scheduled_datetime = dto.scheduled_datetime
    created_scheduling.duration_minutes = dto.duration_minutes
    created_scheduling.price = 100
    created_scheduling.created_at = datetime.now()
    mock_scheduling_repo.create.return_value = created_scheduling

    # Act
    result = await use_case.execute(dto)

    # Assert
    assert result.instructor_id == instructor_id

@pytest.mark.asyncio
async def test_should_succeed_when_cart_is_empty(use_case, mock_scheduling_repo, mock_user_repo, mock_instructor_repo, mock_availability_repo):
    # Arrange
    student_id = uuid4()
    instructor_id = uuid4()
    
    dto = CreateSchedulingDTO(
        student_id=student_id,
        instructor_id=instructor_id,
        scheduled_datetime=datetime.now(),
        lesson_category="B",
        vehicle_ownership="instructor",
        duration_minutes=60
    )

    # Mock student
    student = MagicMock()
    student.user_type = UserType.STUDENT
    student.is_active = True
    student.full_name = "Student Name"
    mock_user_repo.get_by_id.side_effect = [student, MagicMock(full_name="Inst Name", user_type=UserType.INSTRUCTOR, is_active=True)]

    # Mock EMPTY cart
    mock_scheduling_repo.list_by_student.return_value = []

    # Mock other dependencies
    instructor_profile = MagicMock()
    instructor_profile.is_available = True
    instructor_profile.hourly_rate = 100
    instructor_profile.price_cat_b_instructor_vehicle = 100
    mock_instructor_repo.get_by_user_id.return_value = instructor_profile
    
    mock_availability_repo.is_time_available.return_value = True
    mock_scheduling_repo.check_conflict.return_value = False
    
    created_scheduling = MagicMock(spec=Scheduling)
    created_scheduling.id = uuid4()
    created_scheduling.student_id = student_id
    created_scheduling.instructor_id = instructor_id
    created_scheduling.status = SchedulingStatus.PENDING
    created_scheduling.scheduled_datetime = dto.scheduled_datetime
    created_scheduling.duration_minutes = dto.duration_minutes
    created_scheduling.price = 100
    created_scheduling.created_at = datetime.now()
    mock_scheduling_repo.create.return_value = created_scheduling

    # Act
    result = await use_case.execute(dto)

    # Assert
    assert result.instructor_id == instructor_id
