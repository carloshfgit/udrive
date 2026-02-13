"""
Payment and Scheduling Celery Tasks

Contém as implementações das tarefas em background para manutenção de agendamentos e pagamentos.
"""

import asyncio
import logging
from datetime import datetime, timezone

from src.infrastructure.tasks.celery_app import celery_app
from src.infrastructure.db.database import AsyncSessionLocal, engine
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from src.infrastructure.repositories.instructor_repository_impl import (
    InstructorRepositoryImpl,
)
from src.infrastructure.external.stripe_gateway import StripePaymentGateway
from src.application.use_cases.payment.release_payment import ReleasePaymentUseCase

logger = logging.getLogger(__name__)


async def _expire_stale_reservations() -> None:
    """Implementação assíncrona para expirar reservas de slots."""
    async with AsyncSessionLocal() as session:
        repo = SchedulingRepositoryImpl(session)
        expired_list = await repo.list_expired_reservations()

        if not expired_list:
            return

        logger.info(f"Encontradas {len(expired_list)} reservas expiradas para processar.")

        for scheduling in expired_list:
            try:
                scheduling.expire_reservation()
                await repo.update(scheduling)
                logger.info(f"Reserva {scheduling.id} expirada com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao expirar reserva {scheduling.id}: {e}")

        await session.commit()


@celery_app.task(name="src.infrastructure.tasks.payment_tasks.expire_stale_reservations")
def expire_stale_reservations() -> None:
    """Tarefa Celery para expirar reservas de slots."""
    async def run_task():
        try:
            await _expire_stale_reservations()
        finally:
            await engine.dispose()

    asyncio.run(run_task())


async def _auto_confirm_completed_lessons() -> None:
    """Implementação assíncrona para auto-confirmar aulas e liberar pagamentos (24h após término)."""
    async with AsyncSessionLocal() as session:
        # Repositórios
        scheduling_repo = SchedulingRepositoryImpl(session)
        payment_repo = PaymentRepositoryImpl(session)
        transaction_repo = TransactionRepositoryImpl(session)
        instructor_repo = InstructorRepositoryImpl(session)
        
        # Gateway e Use Case
        gateway = StripePaymentGateway()
        release_payment_use_case = ReleasePaymentUseCase(
            payment_repository=payment_repo,
            transaction_repository=transaction_repo,
            payment_gateway=gateway,
            instructor_repository=instructor_repo,
        )

        # Buscar aulas encerradas há mais de 24h sem confirmação
        lessons = await scheduling_repo.list_unconfirmed_completed_lessons(hours_after_end=24)

        if not lessons:
            return

        logger.info(f"Encontradas {len(lessons)} aulas para auto-confirmação.")

        for scheduling in lessons:
            try:
                # 1. Simular confirmação do aluno (define student_confirmed_at)
                scheduling.student_confirm_completion()
                # 2. Marcar como completo
                scheduling.complete()
                await scheduling_repo.update(scheduling)

                # 3. Liberar pagamento ao instrutor
                await release_payment_use_case.execute(scheduling.id)
                logger.info(f"Aula {scheduling.id} auto-confirmada e pagamento liberado.")
            except Exception as e:
                logger.error(f"Erro na auto-confirmação da aula {scheduling.id}: {e}")

        await session.commit()


@celery_app.task(name="src.infrastructure.tasks.payment_tasks.auto_confirm_completed_lessons")
def auto_confirm_completed_lessons() -> None:
    """Tarefa Celery para auto-confirmar aulas encerradas."""
    async def run_task():
        try:
            await _auto_confirm_completed_lessons()
        finally:
            await engine.dispose()

    asyncio.run(run_task())
