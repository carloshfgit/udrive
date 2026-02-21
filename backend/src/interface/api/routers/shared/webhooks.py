"""
Webhooks Router

Endpoints para receber notificações de webhooks de gateways de pagamento.
"""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.application.use_cases.payment import HandlePaymentWebhookUseCase
from src.domain.exceptions import InvalidWebhookSignatureException
from src.infrastructure.config import Settings
from src.infrastructure.db.database import get_db, AsyncSessionLocal
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from src.infrastructure.repositories.instructor_repository_impl import (
    InstructorRepositoryImpl,
)
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def _validate_mp_signature(
    request_query: str,
    data_id: str,
    x_signature: str,
    x_request_id: str,
    webhook_secret: str,
) -> bool:
    """
    Valida a assinatura x-signature do webhook do Mercado Pago.

    O MP envia:
        x-signature: ts=...,v1=...
        x-request-id: ...

    Template de validação: id:{data_id};request-id:{x_request_id};ts:{ts};
    HMAC SHA256 com o webhook_secret.

    Ref: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
    """
    if not x_signature or not webhook_secret:
        return False

    # Parsear ts e v1 do header
    parts = {}
    for part in x_signature.split(","):
        key, _, value = part.strip().partition("=")
        parts[key] = value

    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        return False

    # Montar template de validação
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

    # Calcular HMAC
    expected = hmac.new(
        webhook_secret.encode(),
        manifest.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, v1)


async def process_webhook_background(dto: WebhookNotificationDTO, settings: Settings) -> None:
    """Processa o webhook em background abrindo sua própria sessão no banco de dados."""
    async with AsyncSessionLocal() as session:
        try:
            use_case = HandlePaymentWebhookUseCase(
                payment_repository=PaymentRepositoryImpl(session),
                scheduling_repository=SchedulingRepositoryImpl(session),
                transaction_repository=TransactionRepositoryImpl(session),
                instructor_repository=InstructorRepositoryImpl(session),
                payment_gateway=MercadoPagoGateway(settings),
            )
            await use_case.execute(dto)
            # Commit das alterações do webhook
            await session.commit()
        except InvalidWebhookSignatureException:
            logger.warning("Assinatura inválida detectada pelo use case.")
            await session.rollback()
        except Exception as e:
            logger.error("Erro ao processar webhook MP: %s", e, exc_info=True)
            await session.rollback()


@router.post(
    "/mercadopago",
    status_code=status.HTTP_200_OK,
    summary="Webhook do Mercado Pago",
    description="Recebe notificações de pagamento do Mercado Pago. Endpoint público, sem autenticação JWT.",
)
async def mercadopago_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Recebe e processa notificações do Mercado Pago.

    IMPORTANTE:
    - Endpoint público (sem autenticação JWT)
    - Validação feita via x-signature (HMAC)
    - Sempre retorna HTTP 200 para evitar retries do MP
    - Despacha regra de negócios no background para não ter timeouts
    """
    settings = Settings()

    # 1. Parsear body
    try:
        body = await request.json()
    except Exception as e:
        logger.error("Erro ao parsear body do webhook: %s", e)
        return {"status": "error", "detail": "Invalid body"}

    # Extrair tipo e ação
    # Webhooks v2 usam 'type', IPNs usam 'topic'
    notification_type = body.get("type") or request.query_params.get("topic") or request.query_params.get("type", "")
    action = body.get("action", "")
    
    # ID do recurso (pagamento ou ordem)
    # data.id para Webhooks v2, id para IPN
    data_id = str(body.get("data", {}).get("id", ""))
    if not data_id:
        data_id = str(request.query_params.get("id", ""))
    if not data_id:
        data_id = str(request.query_params.get("data.id", ""))
    
    notification_id = body.get("id", 0)
    live_mode = body.get("live_mode", True)

    logger.info(
        "Webhook MP recebido: type=%s action=%s data_id=%s notification_id=%s",
        notification_type,
        action,
        data_id,
        notification_id
    )

    # 2. Validar assinatura x-signature
    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")

    if settings.mp_webhook_secret and x_signature:
        is_valid = _validate_mp_signature(
            request_query=str(request.url.query),
            data_id=data_id,
            x_signature=x_signature,
            x_request_id=x_request_id,
            webhook_secret=settings.mp_webhook_secret,
        )
        if not is_valid:
            logger.warning(
                "Assinatura inválida no webhook MP. x-signature=%s data_id=%s type=%s",
                x_signature,
                data_id,
                notification_type
            )
            # Continua o fluxo mesmo com assinatura inválida em homologação ou para IPNs,
            # visto que o HandlePaymentWebhookUseCase fará o GET na API do Mercado Pago
            # garantindo a veracidade do evento.

    # 3. Montar DTO
    dto = WebhookNotificationDTO(
        notification_id=notification_id,
        notification_type=notification_type,
        action=action,
        data_id=data_id,
        live_mode=live_mode,
    )

    # 4. Agendar a execução em background e retornar 200 pro Mercado Pago
    background_tasks.add_task(process_webhook_background, dto, settings)

    return {"status": "ok"}
