"""
Testes unitários para os Scheduling Notification Decorators.

Verifica que os decorators:
1. Delegam corretamente para o use case encapsulado
2. Chamam NotificationService.notify() com os argumentos corretos
3. Nunca bloqueam o fluxo principal mesmo quando notify() falha
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.application.dtos.scheduling_dtos import (
    CancelSchedulingDTO,
    CancellationResultDTO,
    ConfirmSchedulingDTO,
    CreateSchedulingDTO,
    RequestRescheduleDTO,
    RespondRescheduleDTO,
    SchedulingResponseDTO,
)
from src.application.use_cases.scheduling.scheduling_notification_decorators import (
    NotifyOnCancelScheduling,
    NotifyOnConfirmScheduling,
    NotifyOnCreateScheduling,
    NotifyOnRequestReschedule,
    NotifyOnRespondReschedule,
)
from src.domain.entities.notification import NotificationActionType, NotificationType


def make_scheduling_response(**kwargs) -> SchedulingResponseDTO:
    """Helper para criar um SchedulingResponseDTO de teste."""
    defaults = dict(
        id=uuid4(),
        student_id=uuid4(),
        instructor_id=uuid4(),
        scheduled_datetime=datetime(2026, 6, 15, 14, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        price=Decimal("100.00"),
        status="confirmed",
        created_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        student_name="João Aluno",
        instructor_name="Carlos Instrutor",
    )
    defaults.update(kwargs)
    return SchedulingResponseDTO(**defaults)


# =============================================================================
# NotifyOnCreateScheduling
# =============================================================================


class TestNotifyOnCreateScheduling:
    @pytest.mark.asyncio
    async def test_notifies_instructor_on_new_scheduling(self):
        """Deve notificar o instrutor com NEW_SCHEDULING após criação."""
        result = make_scheduling_response()

        wrapped = AsyncMock()
        wrapped.execute.return_value = result

        notification_svc = AsyncMock()

        dto = MagicMock(spec=CreateSchedulingDTO)
        decorator = NotifyOnCreateScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        returned = await decorator.execute(dto)

        assert returned == result
        notification_svc.notify.assert_awaited_once()
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == result.instructor_id
        assert call_kwargs["notification_type"] == NotificationType.NEW_SCHEDULING
        assert call_kwargs["action_type"] == NotificationActionType.SCHEDULING
        assert call_kwargs["action_id"] == result.id
        assert call_kwargs["body"] == "João Aluno agendou uma aula para 15/06 às 11:00h."

    @pytest.mark.asyncio
    async def test_does_not_raise_when_notify_fails(self):
        """Deve retornar o resultado mesmo quando notify() lança exceção."""
        result = make_scheduling_response()

        wrapped = AsyncMock()
        wrapped.execute.return_value = result

        notification_svc = AsyncMock()
        notification_svc.notify.side_effect = RuntimeError("Conexão perdida")

        dto = MagicMock(spec=CreateSchedulingDTO)
        decorator = NotifyOnCreateScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        returned = await decorator.execute(dto)
        assert returned == result  # Fluxo principal não foi bloqueado


# =============================================================================
# NotifyOnConfirmScheduling
# =============================================================================


class TestNotifyOnConfirmScheduling:
    @pytest.mark.asyncio
    async def test_notifies_student_on_confirm(self):
        """Deve notificar o aluno com SCHEDULING_STATUS_CHANGED após confirmação."""
        result = make_scheduling_response(status="confirmed")

        wrapped = AsyncMock()
        wrapped.execute.return_value = result

        notification_svc = AsyncMock()

        dto = MagicMock(spec=ConfirmSchedulingDTO)
        decorator = NotifyOnConfirmScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        with patch.object(decorator, "_schedule_celery_tasks"):
            returned = await decorator.execute(dto)

        assert returned == result
        notification_svc.notify.assert_awaited_once()
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == result.student_id
        assert call_kwargs["notification_type"] == NotificationType.SCHEDULING_STATUS_CHANGED
        assert call_kwargs["body"] == "Carlos Instrutor confirmou sua aula para 15/06 às 11:00h."

    @pytest.mark.asyncio
    async def test_celery_failure_does_not_block_response(self):
        """Falha no agendamento de tasks Celery não bloqueia o retorno."""
        result = make_scheduling_response()
        wrapped = AsyncMock()
        wrapped.execute.return_value = result
        notification_svc = AsyncMock()

        dto = MagicMock(spec=ConfirmSchedulingDTO)
        decorator = NotifyOnConfirmScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        with patch.object(
            decorator, "_schedule_celery_tasks", side_effect=Exception("Redis indisponível")
        ):
            returned = await decorator.execute(dto)

        assert returned == result


# =============================================================================
# NotifyOnCancelScheduling
# =============================================================================


class TestNotifyOnCancelScheduling:
    def _make_scheduling_entity(self, student_id, instructor_id):
        s = MagicMock()
        s.id = uuid4()
        s.student_id = student_id
        s.instructor_id = instructor_id
        return s

    @pytest.mark.asyncio
    async def test_notifies_instructor_when_student_cancels(self):
        """Quando o aluno cancela, o instrutor deve ser notificado."""
        student_id = uuid4()
        instructor_id = uuid4()
        scheduling = self._make_scheduling_entity(student_id, instructor_id)

        cancel_result = CancellationResultDTO(
            scheduling_id=scheduling.id,
            status="cancelled",
            refund_percentage=100,
            refund_amount=Decimal("100.00"),
            cancelled_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )

        wrapped = MagicMock()
        wrapped.scheduling_repository = AsyncMock()
        wrapped.scheduling_repository.get_by_id.return_value = scheduling
        wrapped.execute = AsyncMock(return_value=cancel_result)

        notification_svc = AsyncMock()

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=student_id,
        )
        decorator = NotifyOnCancelScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        with patch.object(decorator, "_revoke_celery_tasks"):
            returned = await decorator.execute(dto)

        assert returned == cancel_result
        notification_svc.notify.assert_awaited_once()
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == instructor_id  # A outra parte

    @pytest.mark.asyncio
    async def test_notifies_student_when_instructor_cancels(self):
        """Quando o instrutor cancela, o aluno deve ser notificado."""
        student_id = uuid4()
        instructor_id = uuid4()
        scheduling = self._make_scheduling_entity(student_id, instructor_id)

        cancel_result = CancellationResultDTO(
            scheduling_id=scheduling.id,
            status="cancelled",
            refund_percentage=100,
            refund_amount=Decimal("100.00"),
            cancelled_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        )

        wrapped = MagicMock()
        wrapped.scheduling_repository = AsyncMock()
        wrapped.scheduling_repository.get_by_id.return_value = scheduling
        wrapped.execute = AsyncMock(return_value=cancel_result)

        notification_svc = AsyncMock()

        dto = CancelSchedulingDTO(
            scheduling_id=scheduling.id,
            cancelled_by=instructor_id,
        )
        decorator = NotifyOnCancelScheduling(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        with patch.object(decorator, "_revoke_celery_tasks"):
            returned = await decorator.execute(dto)

        assert returned == cancel_result
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == student_id  # A outra parte


# =============================================================================
# NotifyOnRequestReschedule
# =============================================================================


class TestNotifyOnRequestReschedule:
    @pytest.mark.asyncio
    async def test_notifies_other_party_on_reschedule_request(self):
        """Deve notificar a outra parte com RESCHEDULE_REQUESTED."""
        student_id = uuid4()
        instructor_id = uuid4()
        result = make_scheduling_response(
            student_id=student_id,
            instructor_id=instructor_id,
            rescheduled_datetime=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
            rescheduled_by=student_id,
        )

        wrapped = AsyncMock()
        wrapped.execute.return_value = result

        notification_svc = AsyncMock()

        dto = RequestRescheduleDTO(
            scheduling_id=result.id,
            user_id=student_id,  # Aluno solicitou
            new_datetime=datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc),
        )
        decorator = NotifyOnRequestReschedule(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        returned = await decorator.execute(dto)

        assert returned == result
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == instructor_id  # Notifica o instrutor
        assert call_kwargs["notification_type"] == NotificationType.RESCHEDULE_REQUESTED
        assert call_kwargs["body"] == "Foi solicitado reagendamento da aula para 20/06 às 07:00h."


# =============================================================================
# NotifyOnRespondReschedule
# =============================================================================


class TestNotifyOnRespondReschedule:
    @pytest.mark.asyncio
    async def test_notifies_requester_on_reschedule_response(self):
        """Deve notificar quem fez a solicitação com RESCHEDULE_RESPONDED."""
        student_id = uuid4()
        instructor_id = uuid4()
        result = make_scheduling_response(
            student_id=student_id,
            instructor_id=instructor_id,
            rescheduled_by=student_id,  # Aluno solicitou
        )

        wrapped = AsyncMock()
        wrapped.execute.return_value = result

        scheduling_repo = AsyncMock()
        scheduling_repo.get_by_id.return_value = MagicMock(rescheduled_by=student_id)
        wrapped.scheduling_repository = scheduling_repo

        notification_svc = AsyncMock()

        dto = RespondRescheduleDTO(
            scheduling_id=result.id,
            user_id=instructor_id,  # Instrutor está respondendo
            accepted=True,
        )
        decorator = NotifyOnRespondReschedule(
            _wrapped=wrapped,
            _notification_service=notification_svc,
        )

        returned = await decorator.execute(dto)

        assert returned == result
        call_kwargs = notification_svc.notify.call_args.kwargs
        assert call_kwargs["user_id"] == student_id  # Quem pediu o reagendamento
        assert call_kwargs["notification_type"] == NotificationType.RESCHEDULE_RESPONDED
