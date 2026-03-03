"""
Refund Tasks

Celery tasks para processamento assíncrono de reembolsos via Mercado Pago.
Utiliza retry automático com backoff para lidar com falhas do MP
(timeout, saldo insuficiente, etc).
"""

import asyncio
import structlog
from src.infrastructure.tasks.celery_app import celery_app
from src.infrastructure.config import settings
from src.application.dtos.payment_dtos import ProcessRefundDTO
from src.application.use_cases.payment.process_refund import ProcessRefundUseCase
from src.infrastructure.repositories.payment_repository_impl import PaymentRepositoryImpl
from src.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
from src.infrastructure.repositories.instructor_repository_impl import InstructorRepositoryImpl
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from uuid import UUID

logger = structlog.get_logger(__name__)


async def _process_refund_logic(payment_id: str, refund_percentage: int, reason: str | None = None):
    """
    Lógica assíncrona para processar o reembolso.
    Cria um engine específico para o worker, garantindo isolamento.
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

    async with session_factory() as session:
        try:
            dto = ProcessRefundDTO(
                payment_id=UUID(payment_id),
                refund_percentage=refund_percentage,
                reason=reason,
            )

            use_case = ProcessRefundUseCase(
                payment_repository=PaymentRepositoryImpl(session),
                transaction_repository=TransactionRepositoryImpl(session),
                instructor_repository=InstructorRepositoryImpl(session),
                payment_gateway=MercadoPagoGateway(settings),
            )

            result = await use_case.execute(dto)
            await session.commit()

            logger.info(
                "celery_refund_success",
                payment_id=payment_id,
                refund_percentage=refund_percentage,
                refund_amount=str(result.refund_amount),
                status=result.status,
            )
            return {
                "payment_id": payment_id,
                "refund_amount": str(result.refund_amount),
                "status": result.status,
            }
        except Exception as e:
            await session.rollback()
            logger.error(
                "celery_refund_processing_error",
                error=str(e),
                payment_id=payment_id,
                refund_percentage=refund_percentage,
            )
            raise e
        finally:
            await engine.dispose()


@celery_app.task(
    name="refund.process",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_refund_task(self, payment_id: str, refund_percentage: int, reason: str | None = None):
    """
    Task Celery para processar reembolso de forma assíncrona.

    Roda num contexto síncrono e encapsula a chamada assíncrona.
    Retry automático (3x com intervalo de 60s) em caso de falha do MP.

    Args:
        payment_id: UUID do Payment (string).
        refund_percentage: Percentual de reembolso (0-100).
        reason: Motivo do cancelamento/reembolso (opcional).
    """
    try:
        result = asyncio.run(_process_refund_logic(payment_id, refund_percentage, reason))
        return f"Refund processed for payment {payment_id}: {result}"
    except Exception as exc:
        logger.error(
            "celery_refund_task_failed",
            error=str(exc),
            payment_id=payment_id,
            retry_count=self.request.retries,
        )
        raise self.retry(exc=exc)
