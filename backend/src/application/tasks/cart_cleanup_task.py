"""
Cart Cleanup Task

Background task que cancela agendamentos expirados no carrinho.
Roda periodicamente via asyncio loop no lifespan do FastAPI.

Regra: agendamentos com status CONFIRMED, sem pagamento concluído,
e com created_at > CART_TIMEOUT_MINUTES são cancelados automaticamente.
O slot do instrutor é liberado e o agendamento some do carrinho do aluno.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker

CART_TIMEOUT_MINUTES = 12
CLEANUP_INTERVAL_SECONDS = 120  # Roda a cada 2 minutos

logger = logging.getLogger(__name__)


async def cleanup_expired_cart_items(session_factory: async_sessionmaker) -> int:
    """
    Cancela agendamentos que estão no carrinho há mais de CART_TIMEOUT_MINUTES.

    Args:
        session_factory: Factory de sessões do SQLAlchemy.

    Returns:
        Número de agendamentos cancelados.
    """
    from src.infrastructure.repositories.scheduling_repository_impl import (
        SchedulingRepositoryImpl,
    )

    cancelled_count = 0

    async with session_factory() as session:
        try:
            repo = SchedulingRepositoryImpl(session)
            expired_items = await repo.get_expired_cart_items(
                timeout_minutes=CART_TIMEOUT_MINUTES
            )

            if not expired_items:
                return 0

            logger.info(
                "cart_cleanup_found_expired",
                count=len(expired_items),
                timeout_minutes=CART_TIMEOUT_MINUTES,
            )

            for scheduling in expired_items:
                try:
                    # Usar student_id como cancelled_by para respeitar FK em users.id
                    scheduling.cancel(
                        cancelled_by=scheduling.student_id,
                        reason=f"Carrinho expirado (timeout de {CART_TIMEOUT_MINUTES} minutos)",
                    )
                    await repo.update(scheduling)
                    cancelled_count += 1

                    logger.info(
                        "cart_item_expired_cancelled",
                        scheduling_id=str(scheduling.id),
                        student_id=str(scheduling.student_id),
                        instructor_id=str(scheduling.instructor_id),
                        created_at=str(scheduling.created_at),
                    )
                except Exception as e:
                    logger.error(
                        "cart_cleanup_item_error",
                        scheduling_id=str(scheduling.id),
                        error=str(e),
                    )

            await session.commit()

            logger.info(
                "cart_cleanup_completed",
                cancelled_count=cancelled_count,
            )
        except Exception as e:
            await session.rollback()
            logger.error("cart_cleanup_error", error=str(e))

    return cancelled_count


async def cart_cleanup_loop(session_factory: async_sessionmaker) -> None:
    """
    Loop infinito que executa a limpeza do carrinho periodicamente.

    Args:
        session_factory: Factory de sessões do SQLAlchemy.
    """
    logger.info(
        "cart_cleanup_loop_started",
        interval_seconds=CLEANUP_INTERVAL_SECONDS,
        timeout_minutes=CART_TIMEOUT_MINUTES,
    )

    while True:
        try:
            await cleanup_expired_cart_items(session_factory)
        except asyncio.CancelledError:
            logger.info("cart_cleanup_loop_cancelled")
            break
        except Exception as e:
            logger.error("cart_cleanup_loop_error", error=str(e))

        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
