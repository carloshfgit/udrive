"""
Unit tests for scheduling reservation logic.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus


class TestSchedulingReservation:
    """Testes para funcionalidade de reserva temporária de slots."""

    @pytest.fixture
    def pending_scheduling(self):
        """Cria um agendamento PENDING básico."""
        return Scheduling(
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            duration_minutes=60,
            price=100.0,
            status=SchedulingStatus.PENDING,
        )

    def test_reserve_from_pending_success(self, pending_scheduling):
        """Deve reservar um agendamento pendente com sucesso."""
        pending_scheduling.reserve(duration_minutes=15)

        assert pending_scheduling.status == SchedulingStatus.RESERVED
        assert pending_scheduling.reserved_until is not None
        # Verifica se o tempo de expiração está no futuro (aprox 15min)
        now = datetime.now(timezone.utc)
        diff = pending_scheduling.reserved_until - now
        assert 14 <= diff.total_seconds() / 60 <= 16

    def test_reserve_from_non_pending_raises_error(self):
        """Não deve permitir reservar agendamento que não esteja PENDING."""
        scheduling = Scheduling(
            student_id=uuid4(),
            instructor_id=uuid4(),
            scheduled_datetime=datetime.now(timezone.utc) + timedelta(days=1),
            duration_minutes=60,
            price=100.0,
            status=SchedulingStatus.CONFIRMED,
        )

        with pytest.raises(ValueError, match="Só é possível reservar um agendamento pendente"):
            scheduling.reserve()

    def test_is_reservation_expired_true(self, pending_scheduling):
        """Deve retornar True se a reserva expirou."""
        pending_scheduling.reserve(duration_minutes=-1)  # Forçar expiração imediata

        assert pending_scheduling.is_reservation_expired() is True

    def test_is_reservation_expired_false(self, pending_scheduling):
        """Deve retornar False se a reserva não expirou."""
        pending_scheduling.reserve(duration_minutes=10)

        assert pending_scheduling.is_reservation_expired() is False

    def test_expire_reservation_success(self, pending_scheduling):
        """Deve expirar uma reserva e mudar status para CANCELLED."""
        pending_scheduling.reserve(duration_minutes=-1)  # Expirado
        
        pending_scheduling.expire_reservation()

        assert pending_scheduling.status == SchedulingStatus.CANCELLED
        assert pending_scheduling.cancellation_reason == "Reserva expirada"
        assert pending_scheduling.cancelled_at is not None

    def test_expire_reservation_not_expired_raises_error(self, pending_scheduling):
        """Deve lançar erro ao tentar expirar reserva ainda válida."""
        pending_scheduling.reserve(duration_minutes=15)

        with pytest.raises(ValueError, match="Reserva ainda não expirou"):
            pending_scheduling.expire_reservation()

    def test_expire_reservation_wrong_status_raises_error(self, pending_scheduling):
        """Deve lançar erro ao tentar expirar algo que não é RESERVED."""
        with pytest.raises(ValueError, match="Só é possível expirar uma reserva"):
            pending_scheduling.expire_reservation()

    def test_can_cancel_includes_reserved(self, pending_scheduling):
        """Verifica se RESERVED está incluso na lista de status canceláveis."""
        pending_scheduling.status = SchedulingStatus.RESERVED
        assert pending_scheduling.can_cancel() is True
