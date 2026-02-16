"""
Webhooks Router

Endpoints para receber notificações de webhooks de gateways de pagamento.
"""

import hashlib
import hmac
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.application.use_cases.payment import HandlePaymentWebhookUseCase
from src.domain.exceptions import InvalidWebhookSignatureException
from src.infrastructure.config import Settings
from src.infrastructure.db.database import get_db
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


@router.post(
    "/mercadopago",
    status_code=status.HTTP_200_OK,
    summary="Webhook do Mercado Pago",
    description="Recebe notificações de pagamento do Mercado Pago. Endpoint público, sem autenticação JWT.",
)
async def mercadopago_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Recebe e processa notificações do Mercado Pago.

    IMPORTANTE:
    - Endpoint público (sem autenticação JWT)
    - Validação feita via x-signature (HMAC)
    - Sempre retorna HTTP 200 para evitar retries do MP
    """
    settings = Settings()

    # 1. Parsear body
    try:
        body = await request.json()
    except Exception as e:
        logger.error("Erro ao parsear body do webhook: %s", e)
        return {"status": "error", "detail": "Invalid body"}

    # Extrair dados relevantes
    notification_type = body.get("type", "")
    action = body.get("action", "")
    data_id = str(body.get("data", {}).get("id", ""))
    notification_id = body.get("id", 0)
    live_mode = body.get("live_mode", True)

    logger.info(
        "Webhook MP recebido: type=%s action=%s data_id=%s",
        notification_type,
        action,
        data_id,
    )

    # 2. Validar assinatura x-signature
    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")

    if settings.mp_webhook_secret:
        is_valid = _validate_mp_signature(
            request_query=str(request.url.query),
            data_id=data_id,
            x_signature=x_signature,
            x_request_id=x_request_id,
            webhook_secret=settings.mp_webhook_secret,
        )
        if not is_valid:
            logger.warning(
                "Assinatura inválida no webhook MP. x-signature=%s", x_signature
            )
            # Retornar 200 mesmo assim para não gerar retries infinitos,
            # mas logar o erro para investigação
            return {"status": "error", "detail": "Invalid signature"}

    # 3. Montar DTO
    dto = WebhookNotificationDTO(
        notification_id=notification_id,
        notification_type=notification_type,
        action=action,
        data_id=data_id,
        live_mode=live_mode,
    )

    # 4. Executar use case
    try:
        use_case = HandlePaymentWebhookUseCase(
            payment_repository=PaymentRepositoryImpl(db),
            scheduling_repository=SchedulingRepositoryImpl(db),
            transaction_repository=TransactionRepositoryImpl(db),
            instructor_repository=InstructorRepositoryImpl(db),
            payment_gateway=MercadoPagoGateway(settings),
        )
        await use_case.execute(dto)
    except InvalidWebhookSignatureException:
        logger.warning("Assinatura inválida detectada pelo use case.")
    except Exception as e:
        # Logar erro mas retornar 200 para o MP não reenviar indefinidamente
        logger.error("Erro ao processar webhook MP: %s", e, exc_info=True)

    # 5. Sempre retornar 200
    return {"status": "ok"}
