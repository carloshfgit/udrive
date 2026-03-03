"""
Lesson Tasks

Celery tasks relacionadas ao gerenciamento automático de aulas.
"""

import asyncio
import structlog
from src.infrastructure.tasks.celery_app import celery_app
from src.application.use_cases.scheduling.auto_complete_lessons import AutoCompleteLessonsUseCase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.config import settings
from src.infrastructure.repositories.scheduling_repository_impl import SchedulingRepositoryImpl

logger = structlog.get_logger(__name__)


async def _run_auto_complete():
    """
    Wrapper assíncrono para a task de auto-complete.
    Cria um engine específico para o loop de eventos atual.
    """
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=5,
        max_overflow=5,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    try:
        async with session_factory() as session:
            async with session.begin():
                repo = SchedulingRepositoryImpl(session)
                use_case = AutoCompleteLessonsUseCase(scheduling_repository=repo)
                return await use_case.execute(hours_threshold=24)
    finally:
        await engine.dispose()


@celery_app.task(
    name="lessons.auto_complete_overdue",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def auto_complete_overdue_lessons(self):
    """
    Task Celery que auto-completa aulas confirmadas com mais de 24h
    após o término previsto, caso o aluno não tenha confirmado nem aberto disputa.
    """
    try:
        completed_count = asyncio.run(_run_auto_complete())

        if completed_count > 0:
            logger.info("celery_auto_complete_success", completed_count=completed_count)
            return f"Auto-completed {completed_count} overdue lessons"

        return "No overdue lessons found"

    except Exception as exc:
        logger.error("celery_auto_complete_failed", error=str(exc))
        raise self.retry(exc=exc)
