import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

from src.application.use_cases.scheduling.clear_student_cart import ClearStudentCartUseCase
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus

@pytest.mark.asyncio
async def test_clear_student_cart_success():
    # Setup
    mock_repo = MagicMock()
    mock_user_repo = MagicMock()
    student_id = uuid4()
    
    # Mock scheduling entity
    scheduling = MagicMock(spec=Scheduling)
    scheduling.id = uuid4()
    scheduling.student_id = student_id
    
    mock_repo.get_expired_cart_items = AsyncMock(return_value=[scheduling])
    mock_repo.update = AsyncMock()
    
    use_case = ClearStudentCartUseCase(mock_repo, mock_user_repo)
    
    # Execute
    count = await use_case.execute(student_id)
    
    # Assert
    assert count == 1
    scheduling.cancel.assert_called_once()
    mock_repo.update.assert_called_once_with(scheduling)
    mock_repo.get_expired_cart_items.assert_called_once_with(
        student_id=student_id,
        timeout_minutes=0
    )

@pytest.mark.asyncio
async def test_clear_student_cart_empty():
    # Setup
    mock_repo = MagicMock()
    mock_user_repo = MagicMock()
    student_id = uuid4()
    
    mock_repo.get_expired_cart_items = AsyncMock(return_value=[])
    
    use_case = ClearStudentCartUseCase(mock_repo, mock_user_repo)
    
    # Execute
    count = await use_case.execute(student_id)
    
    # Assert
    assert count == 0
    mock_repo.get_expired_cart_items.assert_called_once()
