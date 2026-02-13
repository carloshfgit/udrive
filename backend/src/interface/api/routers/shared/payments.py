"""
Shared Payments Router

Endpoints de pagamento compartilhados (webhook Stripe).
"""

import logging

import stripe
from fastapi import APIRouter, HTTPException, Request, status

from src.application.use_cases.payment.handle_stripe_webhook import (
    HandleStripeWebhookUseCase,
)
from src.infrastructure.config import settings
from src.interface.api.dependencies import PaymentRepo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Shared - Payments"])


@router.post(
    "/stripe/webhook",
    status_code=status.HTTP_200_OK,
    summary="Stripe Webhook",
    description="Recebe eventos do Stripe para atualização de status de pagamentos.",
)
async def stripe_webhook(
    request: Request,
    payment_repo: PaymentRepo,
) -> dict:
    """
    Endpoint de webhook do Stripe.

    1. Lê o payload bruto da requisição
    2. Valida a assinatura com o webhook secret
    3. Despacha o evento para o HandleStripeWebhookUseCase

    Returns:
        dict com status do processamento.
    """
    # 1. Ler payload bruto
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header",
        )

    # 2. Validar assinatura
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET não configurado")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except ValueError:
        logger.error("Payload inválido no webhook Stripe")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        )
    except stripe.SignatureVerificationError:
        logger.error("Assinatura inválida no webhook Stripe")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # 3. Processar evento
    logger.info("Webhook Stripe recebido: %s", event["type"])

    use_case = HandleStripeWebhookUseCase(
        payment_repository=payment_repo,
    )

    result = await use_case.execute(
        event_type=event["type"],
        event_data=event["data"]["object"],
    )

    return result
