import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from src.application.use_cases.scheduling.get_next_student_scheduling_use_case import GetNextStudentSchedulingUseCase

@pytest.mark.asyncio
async def test_get_next_student_scheduling_success():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_next_student_scheduling = AsyncMock()
    
    student_id = uuid4()
    mock_scheduling = MagicMock()
    mock_repo.get_next_student_scheduling.return_value = mock_scheduling
    
    use_case = GetNextStudentSchedulingUseCase(mock_repo)
    
    # Act
    result = await use_case.execute(student_id)
    
    # Assert
    assert result == mock_scheduling
    mock_repo.get_next_student_scheduling.assert_called_once_with(student_id)

@pytest.mark.asyncio
async def test_get_next_student_scheduling_none():
    # Arrange
    mock_repo = MagicMock()
    mock_repo.get_next_student_scheduling = AsyncMock()
    
    student_id = uuid4()
    mock_repo.get_next_student_scheduling.return_value = None
    
    use_case = GetNextStudentSchedulingUseCase(mock_repo)
    
    # Act
    result = await use_case.execute(student_id)
    
    # Assert
    assert result is None
    mock_repo.get_next_student_scheduling.assert_called_once_with(student_id)
