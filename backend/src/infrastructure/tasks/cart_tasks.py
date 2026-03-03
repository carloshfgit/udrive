"""
Cart Tasks

Celery tasks relacionadas ao gerenciamento de carrinhos e agendamentos temporários.
"""

import asyncio
import structlog
from src.infrastructure.tasks.celery_app import celery_app
from src.application.tasks.cart_cleanup_task import cleanup_expired_cart_items
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.infrastructure.config import settings

logger = structlog.get_logger(__name__)


async def _run_cleanup():
    """
    Wrapper assíncrono para a task de limpeza.
    Cria um engine específico para o loop de eventos atual, evitando o erro
    'RuntimeError: Event loop is closed' ao reutilizar o pool de conexões do engine global.
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
        return await cleanup_expired_cart_items(session_factory)
    finally:
        await engine.dispose()


@celery_app.task(
    name="cart.cleanup_expired_items",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def cleanup_cart_task(self):
    """
    Task Celery que invoca a limpeza de agendamentos expirados no carrinho.
    Roda num contexto síncrono e encapsula a chamada assíncrona.
    """
    try:
        # A execução da tarefa assíncrona de banco de dados
        cancelled_count = asyncio.run(_run_cleanup())
        
        if cancelled_count > 0:
            logger.info("celery_cart_cleanup_success", cancelled_count=cancelled_count)
            return f"Cancelled {cancelled_count} expired items"
            
        return "No expired items found"
        
    except Exception as exc:
        logger.error("celery_cart_cleanup_failed", error=str(exc))
        raise self.retry(exc=exc)
