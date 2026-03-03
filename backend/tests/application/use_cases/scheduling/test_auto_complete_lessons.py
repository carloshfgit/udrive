"""
Testes para AutoCompleteLessonsUseCase.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.application.use_cases.scheduling.auto_complete_lessons import AutoCompleteLessonsUseCase
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


def _make_overdue_scheduling(**overrides) -> Scheduling:
    """Helper para criar um Scheduling CONFIRMED que terminou há mais de 24h."""
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


@pytest.mark.asyncio
async def test_auto_complete_processes_overdue_lessons():
    """Deve auto-completar aulas atrasadas com sucesso."""
    mock_repo = MagicMock()
    s1 = _make_overdue_scheduling()
    s2 = _make_overdue_scheduling()
    mock_repo.get_overdue_confirmed = AsyncMock(return_value=[s1, s2])
    mock_repo.update = AsyncMock(side_effect=lambda s: s)

    use_case = AutoCompleteLessonsUseCase(scheduling_repository=mock_repo)
    result = await use_case.execute(hours_threshold=24)

    assert result == 2
    assert s1.status == SchedulingStatus.COMPLETED
    assert s2.status == SchedulingStatus.COMPLETED
    assert mock_repo.update.call_count == 2


@pytest.mark.asyncio
async def test_auto_complete_returns_zero_when_no_overdue():
    """Deve retornar 0 quando não há aulas atrasadas."""
    mock_repo = MagicMock()
    mock_repo.get_overdue_confirmed = AsyncMock(return_value=[])

    use_case = AutoCompleteLessonsUseCase(scheduling_repository=mock_repo)
    result = await use_case.execute()

    assert result == 0
    mock_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_auto_complete_continues_on_error():
    """Deve continuar processando mesmo se uma aula falhar."""
    mock_repo = MagicMock()
    s1 = _make_overdue_scheduling(status=SchedulingStatus.CANCELLED)  # vai falhar
    s2 = _make_overdue_scheduling()  # vai funcionar
    mock_repo.get_overdue_confirmed = AsyncMock(return_value=[s1, s2])
    mock_repo.update = AsyncMock(side_effect=lambda s: s)

    use_case = AutoCompleteLessonsUseCase(scheduling_repository=mock_repo)
    result = await use_case.execute()

    assert result == 1  # apenas s2 foi auto-completada
    assert s2.status == SchedulingStatus.COMPLETED


@pytest.mark.asyncio
async def test_auto_complete_does_not_process_disputed():
    """Aulas DISPUTED não devem ser retornadas pelo repo (filtro no SQL),
    mas se chegarem, auto_complete() deve rejeitar."""
    mock_repo = MagicMock()
    disputed = _make_overdue_scheduling(status=SchedulingStatus.DISPUTED)
    mock_repo.get_overdue_confirmed = AsyncMock(return_value=[disputed])
    mock_repo.update = AsyncMock(side_effect=lambda s: s)

    use_case = AutoCompleteLessonsUseCase(scheduling_repository=mock_repo)
    result = await use_case.execute()

    assert result == 0  # falhou porque é DISPUTED
    assert disputed.status == SchedulingStatus.DISPUTED  # não mudou
