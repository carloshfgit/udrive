"""
Notification Celery Tasks

Tarefas agendadas para notificações automáticas:
- send_lesson_reminder: Lembrete 30min antes da aula
- send_review_request: Solicitação de avaliação 1h após a aula

As tasks são síncronas (Celery) mas usam asyncio.run() para
chamar o NotificationService que é assíncrono.
"""

import asyncio
import structlog
from uuid import UUID

from celery import shared_task

from src.domain.entities.notification import NotificationActionType, NotificationType
from src.domain.entities.scheduling_status import SchedulingStatus

logger = structlog.get_logger()


async def _send_lesson_reminder_async(scheduling_id: str) -> None:
    """
    Implementação assíncrona do lembrete de aula.

    Busca o agendamento, verifica status CONFIRMED e notifica
    ambos os participantes (instrutor e aluno).
    """
    from src.application.services.notification_service import NotificationService
    from src.infrastructure.db.database import AsyncSessionLocal
    from src.infrastructure.repositories.notification_repository_impl import (
        NotificationRepositoryImpl,
    )
    from src.infrastructure.repositories.scheduling_repository_impl import (
        SchedulingRepositoryImpl,
    )
    from src.infrastructure.repositories.user_repository_impl import (
        UserRepositoryImpl,
    )
    from src.infrastructure.services.push_notification_service import (
        ExpoPushNotificationService,
    )
    from src.interface.websockets.connection_manager import manager as ws_manager

    async with AsyncSessionLocal() as session:
        # Buscar agendamento
        scheduling_repo = SchedulingRepositoryImpl(session)
        scheduling = await scheduling_repo.get_by_id(UUID(scheduling_id))

        if scheduling is None:
            logger.warning(
                "lesson_reminder_scheduling_not_found",
                scheduling_id=scheduling_id,
            )
            return

        # Verificar se ainda está confirmado (pode ter sido cancelado entretanto)
        if scheduling.status != SchedulingStatus.CONFIRMED:
            logger.info(
                "lesson_reminder_skipped_not_confirmed",
                scheduling_id=scheduling_id,
                status=scheduling.status.value,
            )
            return

        # Buscar nomes dos participantes
        user_repo = UserRepositoryImpl(session)
        student = await user_repo.get_by_id(scheduling.student_id)
        instructor = await user_repo.get_by_id(scheduling.instructor_id)

        student_name = student.full_name if student else "Aluno"
        instructor_name = instructor.full_name if instructor else "Instrutor"

        # Montar o NotificationService
        notification_service = NotificationService(
            notification_repository=NotificationRepositoryImpl(session),
            push_service=ExpoPushNotificationService(session),
            ws_manager=ws_manager,
        )

        # Formatar horário da aula
        hora = scheduling.scheduled_datetime.strftime("%H:%M")

        # Notificar instrutor
        await notification_service.notify(
            user_id=scheduling.instructor_id,
            notification_type=NotificationType.LESSON_REMINDER,
            title="Aula em 30 minutos! ⏰",
            body=f"Sua aula com {student_name} começa às {hora}.",
            action_type=NotificationActionType.SCHEDULING,
            action_id=scheduling.id,
        )

        # Notificar aluno
        await notification_service.notify(
            user_id=scheduling.student_id,
            notification_type=NotificationType.LESSON_REMINDER,
            title="Aula em 30 minutos! ⏰",
            body=f"Sua aula com {instructor_name} começa às {hora}.",
            action_type=NotificationActionType.SCHEDULING,
            action_id=scheduling.id,
        )

        logger.info(
            "lesson_reminder_sent",
            scheduling_id=scheduling_id,
        )


async def _send_review_request_async(scheduling_id: str) -> None:
    """
    Implementação assíncrona da solicitação de avaliação.

    Busca o agendamento, verifica status COMPLETED e notifica
    o aluno para avaliar o instrutor.
    """
    from src.application.services.notification_service import NotificationService
    from src.infrastructure.db.database import AsyncSessionLocal
    from src.infrastructure.repositories.notification_repository_impl import (
        NotificationRepositoryImpl,
    )
    from src.infrastructure.repositories.review_repository_impl import (
        ReviewRepositoryImpl,
    )
    from src.infrastructure.repositories.scheduling_repository_impl import (
        SchedulingRepositoryImpl,
    )
    from src.infrastructure.repositories.user_repository_impl import (
        UserRepositoryImpl,
    )
    from src.infrastructure.services.push_notification_service import (
        ExpoPushNotificationService,
    )
    from src.interface.websockets.connection_manager import manager as ws_manager

    async with AsyncSessionLocal() as session:
        # Buscar agendamento
        scheduling_repo = SchedulingRepositoryImpl(session)
        scheduling = await scheduling_repo.get_by_id(UUID(scheduling_id))

        if scheduling is None:
            logger.warning(
                "review_request_scheduling_not_found",
                scheduling_id=scheduling_id,
            )
            return

        # Verificar se está concluído
        if scheduling.status != SchedulingStatus.COMPLETED:
            logger.info(
                "review_request_skipped_not_completed",
                scheduling_id=scheduling_id,
                status=scheduling.status.value,
            )
            return

        # Verificar se já existe review para esse agendamento
        review_repo = ReviewRepositoryImpl(session)
        existing_review = await review_repo.get_by_scheduling_id(scheduling.id)
        if existing_review is not None:
            logger.info(
                "review_request_skipped_already_reviewed",
                scheduling_id=scheduling_id,
            )
            return

        # Buscar nome do instrutor
        user_repo = UserRepositoryImpl(session)
        instructor = await user_repo.get_by_id(scheduling.instructor_id)
        instructor_name = instructor.full_name if instructor else "instrutor"

        # Montar o NotificationService
        notification_service = NotificationService(
            notification_repository=NotificationRepositoryImpl(session),
            push_service=ExpoPushNotificationService(session),
            ws_manager=ws_manager,
        )

        # Notificar aluno
        await notification_service.notify(
            user_id=scheduling.student_id,
            notification_type=NotificationType.REVIEW_REQUEST,
            title="Como foi sua aula? ⭐",
            body=f"Avalie sua experiência com {instructor_name}.",
            action_type=NotificationActionType.REVIEW,
            action_id=scheduling.id,
        )

        logger.info(
            "review_request_sent",
            scheduling_id=scheduling_id,
        )


@shared_task(name="send_lesson_reminder")
def send_lesson_reminder(scheduling_id: str) -> None:
    """
    Envia lembrete de aula para ambos os participantes.
    Agendada para disparar 30min antes da aula.

    Args:
        scheduling_id: UUID do agendamento como string.
    """
    asyncio.run(_send_lesson_reminder_async(scheduling_id))


@shared_task(name="send_review_request")
def send_review_request(scheduling_id: str) -> None:
    """
    Notifica o aluno para avaliar o instrutor.
    Agendada para 1h após o término da aula.

    Args:
        scheduling_id: UUID do agendamento como string.
    """
    asyncio.run(_send_review_request_async(scheduling_id))
