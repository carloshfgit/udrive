"""
Webhook Tasks

Celery tasks relacionadas ao processamento de notificações de webhooks de gateways de pagamento.
"""

import asyncio
import structlog
from typing import Any
from src.infrastructure.tasks.celery_app import celery_app
from src.infrastructure.config import settings
from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.application.use_cases.payment import HandlePaymentWebhookUseCase
from src.infrastructure.repositories.payment_repository_impl import PaymentRepositoryImpl
from src.infrastructure.repositories.scheduling_repository_impl import SchedulingRepositoryImpl
from src.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
from src.infrastructure.repositories.instructor_repository_impl import InstructorRepositoryImpl
from src.infrastructure.repositories.notification_repository_impl import NotificationRepositoryImpl
from src.infrastructure.services.push_notification_service import ExpoPushNotificationService
from src.application.services.notification_service import NotificationService
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from src.interface.websockets.connection_manager import manager as ws_manager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

logger = structlog.get_logger(__name__)

async def _process_mercadopago_logic(notification_dict: dict[str, Any]):
    """
    Lógica assíncrona para processar o webhook do Mercado Pago.
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
            dto = WebhookNotificationDTO(**notification_dict)
            
            notification_service = NotificationService(
                notification_repository=NotificationRepositoryImpl(session),
                push_service=ExpoPushNotificationService(session),
                ws_manager=ws_manager,
            )

            use_case = HandlePaymentWebhookUseCase(
                payment_repository=PaymentRepositoryImpl(session),
                scheduling_repository=SchedulingRepositoryImpl(session),
                transaction_repository=TransactionRepositoryImpl(session),
                instructor_repository=InstructorRepositoryImpl(session),
                payment_gateway=MercadoPagoGateway(settings),
                notification_service=notification_service,
            )
            
            await use_case.execute(dto)
            # Commit das alterações do webhook
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error("celery_webhook_processing_error", error=str(e), notification=notification_dict)
            raise e
        finally:
            await engine.dispose()

@celery_app.task(
    name="webhook.process_mercadopago",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def process_mercadopago_webhook(self, notification_dict: dict[str, Any]):
    """
    Task Celery para processar webhook do Mercado Pago.
    Roda num contexto síncrono e encapsula a chamada assíncrona.
    """
    try:
        asyncio.run(_process_mercadopago_logic(notification_dict))
        return f"Successfully processed notification {notification_dict.get('notification_id')}"
    except Exception as exc:
        logger.error("celery_mercadopago_webhook_failed", error=str(exc))
        raise self.retry(exc=exc)
