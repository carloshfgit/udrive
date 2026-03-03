"""
Scheduling Notification Decorators

Decorators que envolvem os use cases de scheduling e disparam notificações
após execução bem-sucedida, mantendo os use cases originais desacoplados.

Padrão:
    1. Delega ao use case encapsulado
    2. Extrai dados do resultado
    3. Chama NotificationService.notify() nos destinatários corretos
    4. Erros de notificação são capturados para nunca bloquear o fluxo principal
"""

import structlog
from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.scheduling_dtos import (
    CancelSchedulingDTO,
    CancellationResultDTO,
    ConfirmSchedulingDTO,
    CreateSchedulingDTO,
    RequestRescheduleDTO,
    RespondRescheduleDTO,
    SchedulingResponseDTO,
)
from src.application.services.notification_service import NotificationService
from src.application.use_cases.scheduling.cancel_scheduling import CancelSchedulingUseCase
from src.application.use_cases.scheduling.confirm_scheduling import ConfirmSchedulingUseCase
from src.application.use_cases.scheduling.create_scheduling import CreateSchedulingUseCase
from src.application.use_cases.scheduling.request_reschedule_use_case import RequestRescheduleUseCase
from src.application.use_cases.scheduling.respond_reschedule_use_case import RespondRescheduleUseCase
from src.domain.entities.notification import NotificationActionType, NotificationType

logger = structlog.get_logger()


@dataclass
class NotifyOnCreateScheduling:
    """
    Decorator de CreateSchedulingUseCase.

    Após criação bem-sucedida, notifica o instrutor com NEW_SCHEDULING.
    """

    _wrapped: CreateSchedulingUseCase
    _notification_service: NotificationService

    async def execute(self, dto: CreateSchedulingDTO) -> SchedulingResponseDTO:
        result = await self._wrapped.execute(dto)

        try:
            scheduled_at = result.scheduled_datetime.strftime("%d/%m às %H:%Mh")
            await self._notification_service.notify(
                user_id=result.instructor_id,
                notification_type=NotificationType.NEW_SCHEDULING,
                title="Nova aula agendada! 🎉",
                body=f"{result.student_name} agendou uma aula para {scheduled_at}.",
                action_type=NotificationActionType.SCHEDULING,
                action_id=result.id,
            )
        except Exception:
            logger.exception(
                "notify_on_create_scheduling_failed",
                scheduling_id=str(result.id),
            )

        return result


@dataclass
class NotifyOnConfirmScheduling:
    """
    Decorator de ConfirmSchedulingUseCase.

    Após confirmação bem-sucedida:
    - Notifica o aluno com SCHEDULING_STATUS_CHANGED.
    - Agenda tasks Celery de lembrete (30min antes) e avaliação (1h após).
    """

    _wrapped: ConfirmSchedulingUseCase
    _notification_service: NotificationService

    async def execute(self, dto: ConfirmSchedulingDTO) -> SchedulingResponseDTO:
        result = await self._wrapped.execute(dto)

        try:
            scheduled_at = result.scheduled_datetime.strftime("%d/%m às %H:%Mh")
            await self._notification_service.notify(
                user_id=result.student_id,
                notification_type=NotificationType.SCHEDULING_STATUS_CHANGED,
                title="Aula confirmada! ✅",
                body=f"{result.instructor_name} confirmou sua aula para {scheduled_at}.",
                action_type=NotificationActionType.SCHEDULING,
                action_id=result.id,
            )
        except Exception:
            logger.exception(
                "notify_on_confirm_scheduling_failed",
                scheduling_id=str(result.id),
            )

        # Agendar tasks Celery de lembrete e avaliação
        try:
            self._schedule_celery_tasks(result)
        except Exception:
            logger.exception(
                "celery_task_scheduling_failed",
                scheduling_id=str(result.id),
            )

        return result

    def _schedule_celery_tasks(self, result: SchedulingResponseDTO) -> None:
        """Agenda tasks de lembrete (30min antes) e avaliação (1h após a aula)."""
        from datetime import timedelta

        from src.infrastructure.tasks.notification_tasks import (
            send_lesson_reminder,
            send_review_request,
        )

        # Lembrete: 30 minutos antes da aula
        reminder_eta = result.scheduled_datetime - timedelta(minutes=30)
        send_lesson_reminder.apply_async(
            args=[str(result.id)],
            eta=reminder_eta,
            task_id=f"reminder-{result.id}",
        )

        # Avaliação: 1h após o término da aula
        duration = result.duration_minutes or 60
        lesson_end = result.scheduled_datetime + timedelta(minutes=duration)
        review_eta = lesson_end + timedelta(hours=1)
        send_review_request.apply_async(
            args=[str(result.id)],
            eta=review_eta,
            task_id=f"review-{result.id}",
        )

        logger.info(
            "celery_tasks_scheduled",
            scheduling_id=str(result.id),
            reminder_eta=str(reminder_eta),
            review_eta=str(review_eta),
        )


@dataclass
class NotifyOnCancelScheduling:
    """
    Decorator de CancelSchedulingUseCase.

    Após cancelamento bem-sucedido:
    - Notifica a outra parte com SCHEDULING_STATUS_CHANGED.
    - Revoga tasks Celery pendentes de lembrete e avaliação.

    Requer o scheduling_repository para buscar student_id/instructor_id
    (o CancellationResultDTO não os expõe por design).
    """

    _wrapped: CancelSchedulingUseCase
    _notification_service: NotificationService

    async def execute(self, dto: CancelSchedulingDTO) -> CancellationResultDTO:
        # Precisamos dos participantes antes de cancelar (o use case só retorna IDs e status)
        scheduling = await self._wrapped.scheduling_repository.get_by_id(dto.scheduling_id)

        result = await self._wrapped.execute(dto)

        if scheduling is not None:
            try:
                # Determinar quem recebe a notificação (a outra parte)
                recipient_id = (
                    scheduling.instructor_id
                    if dto.cancelled_by == scheduling.student_id
                    else scheduling.student_id
                )
                await self._notification_service.notify(
                    user_id=recipient_id,
                    notification_type=NotificationType.SCHEDULING_STATUS_CHANGED,
                    title="Aula cancelada ❌",
                    body="Uma aula foi cancelada. Acesse os detalhes para mais informações.",
                    action_type=NotificationActionType.SCHEDULING,
                    action_id=result.scheduling_id,
                )
            except Exception:
                logger.exception(
                    "notify_on_cancel_scheduling_failed",
                    scheduling_id=str(result.scheduling_id),
                )

            # Revogar tasks Celery pendentes
            try:
                self._revoke_celery_tasks(scheduling.id)
            except Exception:
                logger.exception(
                    "celery_task_revoke_failed",
                    scheduling_id=str(scheduling.id),
                )

        return result

    def _revoke_celery_tasks(self, scheduling_id: UUID) -> None:
        """Revoga tasks pendentes de lembrete e avaliação."""
        from src.infrastructure.tasks.celery_app import celery_app

        celery_app.control.revoke(f"reminder-{scheduling_id}", terminate=True)
        celery_app.control.revoke(f"review-{scheduling_id}", terminate=True)
        logger.info("celery_tasks_revoked", scheduling_id=str(scheduling_id))


@dataclass
class NotifyOnRequestReschedule:
    """
    Decorator de RequestRescheduleUseCase.

    Após solicitação de reagendamento bem-sucedida, notifica a outra parte
    com RESCHEDULE_REQUESTED.
    """

    _wrapped: RequestRescheduleUseCase
    _notification_service: NotificationService

    async def execute(self, dto: RequestRescheduleDTO) -> SchedulingResponseDTO:
        result = await self._wrapped.execute(dto)

        try:
            # Notifica a outra parte (não quem solicitou)
            recipient_id = (
                result.instructor_id
                if dto.user_id == result.student_id
                else result.student_id
            )
            new_dt = result.rescheduled_datetime
            date_str = (
                new_dt.strftime("%d/%m às %H:%Mh") if new_dt else "nova data"
            )
            await self._notification_service.notify(
                user_id=recipient_id,
                notification_type=NotificationType.RESCHEDULE_REQUESTED,
                title="Solicitação de reagendamento 🔄",
                body=f"Foi solicitado reagendamento da aula para {date_str}.",
                action_type=NotificationActionType.SCHEDULING,
                action_id=result.id,
            )
        except Exception:
            logger.exception(
                "notify_on_request_reschedule_failed",
                scheduling_id=str(result.id),
            )

        return result


@dataclass
class NotifyOnRespondReschedule:
    """
    Decorator de RespondRescheduleUseCase.

    Após resposta ao reagendamento, notifica quem fez a solicitação original
    com RESCHEDULE_RESPONDED.
    """

    _wrapped: RespondRescheduleUseCase
    _notification_service: NotificationService

    async def execute(self, dto: RespondRescheduleDTO) -> SchedulingResponseDTO:
        result = await self._wrapped.execute(dto)

        try:
            # Notifica quem fez a solicitação original
            # rescheduled_by é quem pediu o reagendamento
            requester_id = result.rescheduled_by
            if requester_id is not None:
                action_verb = "aceito" if dto.accepted else "recusado"
                await self._notification_service.notify(
                    user_id=requester_id,
                    notification_type=NotificationType.RESCHEDULE_RESPONDED,
                    title=f"Reagendamento {action_verb} {'✅' if dto.accepted else '❌'}",
                    body=f"Sua solicitação de reagendamento foi {action_verb}.",
                    action_type=NotificationActionType.SCHEDULING,
                    action_id=result.id,
                )
        except Exception:
            logger.exception(
                "notify_on_respond_reschedule_failed",
                scheduling_id=str(result.id),
            )

        return result
