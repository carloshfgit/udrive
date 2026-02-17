"""
Internal Router

Endpoints internos para tarefas automáticas (cron jobs, schedulers).
Devem ser protegidos e não expostos publicamente.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.scheduling.auto_complete_lessons import (
    AutoCompleteLessonsUseCase,
)
from src.infrastructure.db.database import get_db
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/internal", tags=["Internal"])


async def verify_internal_key(
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
) -> None:
    """Verifica chave interna para endpoints protegidos."""
    if x_internal_key != settings.internal_api_key:
        raise HTTPException(status_code=403, detail="Chave interna inválida")


@router.post(
    "/auto-complete-lessons",
    summary="Auto-completar aulas",
    description="Marca aulas como concluídas quando o aluno não confirma em 24h.",
    dependencies=[Depends(verify_internal_key)],
)
async def auto_complete_lessons(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Endpoint para cron job de auto-completar aulas."""
    scheduling_repo = SchedulingRepositoryImpl(db)

    use_case = AutoCompleteLessonsUseCase(
        scheduling_repository=scheduling_repo,
    )

    completed_count = await use_case.execute()

    logger.info(f"Auto-complete executado: {completed_count} aulas completadas.")

    return {
        "completed_count": completed_count,
        "message": f"{completed_count} aula(s) auto-completada(s).",
    }
