"""
Testes unitários para o ResolveDisputeUseCase (Fase 5 – reembolso seletivo).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from uuid import uuid4
from datetime import datetime, timezone

from src.application.use_cases.scheduling.resolve_dispute import (
    ResolveDisputeUseCase,
    DisputeNotFoundException,
)
from src.application.dtos.dispute_dtos import ResolveDisputeDTO, DisputeResponseDTO
from src.domain.entities.dispute_enums import (
    DisputeReason,
    DisputeResolution,
    DisputeStatus,
)


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _make_dispute_mock(dispute_id=None, scheduling_id=None):
    """Cria um mock de Dispute com todos os atributos que o UseCase acessa."""
    d = MagicMock()
    d.id = dispute_id or uuid4()
    d.scheduling_id = scheduling_id or uuid4()
    d.opened_by = uuid4()
    d.reason = DisputeReason.NO_SHOW
    d.description = "Descrição teste"
    d.contact_phone = "11999999999"
    d.contact_email = "aluno@test.com"
    d.status = DisputeStatus.OPEN
    d.resolution = None
    d.resolution_notes = None
    d.refund_type = None
    d.resolved_by = None
    d.resolved_at = None
    d.created_at = datetime.now(timezone.utc)
    d.updated_at = None
    return d


def _make_scheduling_mock(scheduling_id=None):
    """Cria um mock de Scheduling com os atributos usados pelo DTO de resposta."""
    s = MagicMock()
    s.id = scheduling_id or uuid4()
    s.scheduled_datetime = datetime.now(timezone.utc)
    s.student_name = "Aluno Teste"
    s.instructor_name = "Instrutor Teste"
    return s


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def dispute_repo():
    return AsyncMock()


@pytest.fixture
def scheduling_repo():
    return AsyncMock()


@pytest.fixture
def refund_use_case():
    return AsyncMock()


@pytest.fixture
def use_case(dispute_repo, scheduling_repo, refund_use_case):
    return ResolveDisputeUseCase(
        dispute_repository=dispute_repo,
        scheduling_repository=scheduling_repo,
        refund_use_case=refund_use_case,
    )


# ──────────────────────────────────────────────────────────────────
# 1) Reembolso seletivo (payment_ids_to_refund fornecidos)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_favor_student_selective_refunds(
    use_case, dispute_repo, scheduling_repo, refund_use_case,
):
    scheduling_id = uuid4()
    dispute = _make_dispute_mock(scheduling_id=scheduling_id)
    scheduling = _make_scheduling_mock(scheduling_id=scheduling_id)

    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = scheduling

    payment_ids = [uuid4(), uuid4()]

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.FAVOR_STUDENT,
        resolution_notes="Refund selective",
        refund_type="full",
        payment_ids_to_refund=payment_ids,
    )

    result = await use_case.execute(dto)

    # Resolve chamado com os params corretos
    dispute.resolve.assert_called_once()
    scheduling.resolve_dispute_favor_student.assert_called_once()

    # refund_use_case deve ter sido chamado uma vez por payment_id
    assert refund_use_case.execute.call_count == len(payment_ids)

    # Repos salvos
    dispute_repo.update.assert_called_once_with(dispute)
    scheduling_repo.update.assert_called_once_with(scheduling)

    # Retorno é DisputeResponseDTO
    assert isinstance(result, DisputeResponseDTO)


# ──────────────────────────────────────────────────────────────────
# 2) Sem payment_ids → nenhuma chamada de refund (comportamento legado)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_favor_student_no_payment_ids(
    use_case, dispute_repo, scheduling_repo, refund_use_case,
):
    scheduling_id = uuid4()
    dispute = _make_dispute_mock(scheduling_id=scheduling_id)
    scheduling = _make_scheduling_mock(scheduling_id=scheduling_id)

    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = scheduling

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.FAVOR_STUDENT,
        resolution_notes="Sem IDs",
        refund_type="full",
        # payment_ids_to_refund omitido → None
    )

    result = await use_case.execute(dto)

    scheduling.resolve_dispute_favor_student.assert_called_once()
    # Sem payment_ids, nenhum refund é disparado
    refund_use_case.execute.assert_not_called()
    assert isinstance(result, DisputeResponseDTO)


# ──────────────────────────────────────────────────────────────────
# 3) Resolução FAVOR_INSTRUCTOR (sem reembolso)
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_favor_instructor(
    use_case, dispute_repo, scheduling_repo, refund_use_case,
):
    scheduling_id = uuid4()
    dispute = _make_dispute_mock(scheduling_id=scheduling_id)
    scheduling = _make_scheduling_mock(scheduling_id=scheduling_id)

    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = scheduling

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.FAVOR_INSTRUCTOR,
        resolution_notes="Favor instrutor",
    )

    result = await use_case.execute(dto)

    scheduling.resolve_dispute_favor_instructor.assert_called_once()
    refund_use_case.execute.assert_not_called()
    assert isinstance(result, DisputeResponseDTO)


# ──────────────────────────────────────────────────────────────────
# 4) Resolução RESCHEDULED
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_rescheduled(
    use_case, dispute_repo, scheduling_repo, refund_use_case,
):
    scheduling_id = uuid4()
    dispute = _make_dispute_mock(scheduling_id=scheduling_id)
    scheduling = _make_scheduling_mock(scheduling_id=scheduling_id)

    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = scheduling

    new_dt = datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.RESCHEDULED,
        resolution_notes="Reagendado",
        new_datetime=new_dt,
    )

    result = await use_case.execute(dto)

    scheduling.resolve_dispute_reschedule.assert_called_once_with(new_dt)
    refund_use_case.execute.assert_not_called()
    assert isinstance(result, DisputeResponseDTO)


# ──────────────────────────────────────────────────────────────────
# 5) RESCHEDULED sem new_datetime → ValueError
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_rescheduled_missing_datetime(
    use_case, dispute_repo, scheduling_repo,
):
    scheduling_id = uuid4()
    dispute = _make_dispute_mock(scheduling_id=scheduling_id)
    scheduling = _make_scheduling_mock(scheduling_id=scheduling_id)

    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = scheduling

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.RESCHEDULED,
        resolution_notes="Sem data",
        # new_datetime ausente
    )

    with pytest.raises(ValueError, match="Nova data é obrigatória"):
        await use_case.execute(dto)


# ──────────────────────────────────────────────────────────────────
# 6) Disputa não encontrada → DisputeNotFoundException
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_dispute_not_found(use_case, dispute_repo):
    dispute_repo.get_by_id.return_value = None

    dto = ResolveDisputeDTO(
        dispute_id=uuid4(),
        admin_id=uuid4(),
        resolution=DisputeResolution.FAVOR_STUDENT,
        resolution_notes="Notes",
    )

    with pytest.raises(DisputeNotFoundException):
        await use_case.execute(dto)


# ──────────────────────────────────────────────────────────────────
# 7) Scheduling associado não encontrado → ValueError
# ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_resolve_scheduling_not_found(use_case, dispute_repo, scheduling_repo):
    dispute = _make_dispute_mock()
    dispute_repo.get_by_id.return_value = dispute
    scheduling_repo.get_by_id.return_value = None

    dto = ResolveDisputeDTO(
        dispute_id=dispute.id,
        admin_id=uuid4(),
        resolution=DisputeResolution.FAVOR_STUDENT,
        resolution_notes="Notes",
    )

    with pytest.raises(ValueError, match="Agendamento associado não encontrado"):
        await use_case.execute(dto)
