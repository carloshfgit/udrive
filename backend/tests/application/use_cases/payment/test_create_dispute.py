import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from decimal import Decimal

from src.application.use_cases.payment.create_dispute import CreateDisputeUseCase
from src.application.dtos.payment_dtos import CreateDisputeDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.entities.payment_status import PaymentStatus
from src.domain.exceptions import DomainException

@pytest.mark.asyncio
async def test_create_dispute_success():
    # Setup
    scheduling_repo = AsyncMock()
    payment_repo = AsyncMock()
    
    student_id = uuid4()
    scheduling_id = uuid4()
    
    scheduling = MagicMock()
    scheduling.student_id = student_id
    
    payment = MagicMock()
    payment.status = "held"
    
    scheduling_repo.get_by_id.return_value = scheduling
    payment_repo.get_by_scheduling_id.return_value = payment
    
    use_case = CreateDisputeUseCase(scheduling_repo, payment_repo)
    dto = CreateDisputeDTO(scheduling_id=scheduling_id, reason="Instrutor não apareceu", student_id=student_id)
    
    # Execute
    await use_case.execute(dto)
    
    # Assert
    scheduling.mark_disputed.assert_called_once()
    payment.mark_disputed.assert_called_once()
    scheduling_repo.update.assert_called_once_with(scheduling)
    payment_repo.update.assert_called_once_with(payment)

@pytest.mark.asyncio
async def test_create_dispute_unauthorized():
    # Setup
    scheduling_repo = AsyncMock()
    payment_repo = AsyncMock()
    
    student_id = uuid4()
    other_student_id = uuid4()
    scheduling_id = uuid4()
    
    scheduling = MagicMock()
    scheduling.student_id = other_student_id
    
    scheduling_repo.get_by_id.return_value = scheduling
    
    use_case = CreateDisputeUseCase(scheduling_repo, payment_repo)
    dto = CreateDisputeDTO(scheduling_id=scheduling_id, reason="...", student_id=student_id)
    
    # Execute & Assert
    with pytest.raises(DomainException, match="não pertence a este aluno"):
        await use_case.execute(dto)
