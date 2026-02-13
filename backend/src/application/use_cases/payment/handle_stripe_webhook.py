"""
Handle Stripe Webhook Use Case

Caso de uso para processar eventos recebidos do Stripe via webhook.
Cada evento é despachado para um handler específico.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal

from src.domain.entities.payment_status import PaymentStatus
from src.domain.interfaces.payment_repository import IPaymentRepository

logger = logging.getLogger(__name__)


@dataclass
class HandleStripeWebhookUseCase:
    """
    Caso de uso para processar webhooks do Stripe.

    Eventos suportados:
        - payment_intent.succeeded → Payment.mark_held() (escrow)
        - payment_intent.payment_failed → Payment.mark_failed()
        - charge.refunded → Atualiza status de refund
        - account.updated → Log de atualização de conta Connect
    """

    payment_repository: IPaymentRepository

    async def execute(self, event_type: str, event_data: dict) -> dict:
        """
        Despacha o evento para o handler correto.

        Args:
            event_type: Tipo do evento Stripe (ex: 'payment_intent.succeeded').
            event_data: Dados do evento (object do evento).

        Returns:
            dict com resultado do processamento.
        """
        handlers = {
            "payment_intent.succeeded": self._handle_payment_intent_succeeded,
            "payment_intent.payment_failed": self._handle_payment_intent_failed,
            "charge.refunded": self._handle_charge_refunded,
            "account.updated": self._handle_account_updated,
        }

        handler = handlers.get(event_type)
        if handler is None:
            logger.info("Evento Stripe não tratado: %s", event_type)
            return {"status": "ignored", "event_type": event_type}

        try:
            result = await handler(event_data)
            return {"status": "processed", "event_type": event_type, **result}
        except Exception as e:
            logger.error(
                "Erro ao processar webhook Stripe: %s - %s",
                event_type,
                str(e),
            )
            return {"status": "error", "event_type": event_type, "error": str(e)}

    async def _handle_payment_intent_succeeded(self, data: dict) -> dict:
        """
        Handler: payment_intent.succeeded.

        Quando o Stripe confirma que o pagamento foi bem-sucedido,
        move o Payment de PROCESSING → HELD (custódia).
        """
        payment_intent_id = data.get("id")
        if not payment_intent_id:
            return {"detail": "missing payment_intent id"}

        payment = await self.payment_repository.get_by_stripe_payment_intent_id(
            payment_intent_id
        )
        if payment is None:
            logger.warning(
                "Payment não encontrado para PI %s", payment_intent_id
            )
            return {"detail": f"payment not found for PI {payment_intent_id}"}

        if payment.status == PaymentStatus.PROCESSING:
            payment.mark_held()
            await self.payment_repository.update(payment)
            logger.info(
                "Pagamento %s marcado como HELD (PI: %s)",
                payment.id,
                payment_intent_id,
            )
            return {"payment_id": str(payment.id), "new_status": "held"}

        logger.warning(
            "Pagamento %s em status %s inesperado para PI.succeeded",
            payment.id,
            payment.status.value,
        )
        return {
            "payment_id": str(payment.id),
            "detail": f"already in {payment.status.value}",
        }

    async def _handle_payment_intent_failed(self, data: dict) -> dict:
        """
        Handler: payment_intent.payment_failed.

        Quando pagamento falha no Stripe, marca Payment como FAILED.
        """
        payment_intent_id = data.get("id")
        if not payment_intent_id:
            return {"detail": "missing payment_intent id"}

        payment = await self.payment_repository.get_by_stripe_payment_intent_id(
            payment_intent_id
        )
        if payment is None:
            logger.warning(
                "Payment não encontrado para PI %s", payment_intent_id
            )
            return {"detail": f"payment not found for PI {payment_intent_id}"}

        if payment.status in (PaymentStatus.PROCESSING, PaymentStatus.PENDING):
            payment.mark_failed()
            await self.payment_repository.update(payment)
            logger.info(
                "Pagamento %s marcado como FAILED (PI: %s)",
                payment.id,
                payment_intent_id,
            )
            return {"payment_id": str(payment.id), "new_status": "failed"}

        return {
            "payment_id": str(payment.id),
            "detail": f"already in {payment.status.value}",
        }

    async def _handle_charge_refunded(self, data: dict) -> dict:
        """
        Handler: charge.refunded.

        Atualiza o status de reembolso no Payment quando Stripe confirma.
        """
        payment_intent_id = data.get("payment_intent")
        if not payment_intent_id:
            return {"detail": "missing payment_intent in charge data"}

        payment = await self.payment_repository.get_by_stripe_payment_intent_id(
            payment_intent_id
        )
        if payment is None:
            logger.warning(
                "Payment não encontrado para charge.refunded (PI: %s)",
                payment_intent_id,
            )
            return {"detail": f"payment not found for PI {payment_intent_id}"}

        # Verificar se o reembolso já foi registrado pelo nosso use case
        if payment.is_refunded:
            logger.info(
                "Reembolso já registrado para pagamento %s", payment.id
            )
            return {
                "payment_id": str(payment.id),
                "detail": "refund already recorded",
            }

        # Atualizar com o valor do reembolso do Stripe
        amount_refunded = data.get("amount_refunded", 0)
        if amount_refunded > 0:
            refund_amount_brl = Decimal(amount_refunded) / 100
            total_amount_cents = int(payment.amount * 100)

            if amount_refunded >= total_amount_cents:
                payment.process_refund(100)
            else:
                percentage = int((amount_refunded / total_amount_cents) * 100)
                payment.process_refund(percentage)

            await self.payment_repository.update(payment)
            logger.info(
                "Reembolso Stripe processado para pagamento %s: R$%.2f",
                payment.id,
                refund_amount_brl,
            )
            return {
                "payment_id": str(payment.id),
                "new_status": payment.status.value,
                "refund_amount": str(refund_amount_brl),
            }

        return {"payment_id": str(payment.id), "detail": "no amount refunded"}

    async def _handle_account_updated(self, data: dict) -> dict:
        """
        Handler: account.updated.

        Loga atualizações de contas Connect (onboarding, status de pagamentos).
        Pode ser estendido para atualizar status no banco.
        """
        account_id = data.get("id")
        charges_enabled = data.get("charges_enabled", False)
        payouts_enabled = data.get("payouts_enabled", False)
        details_submitted = data.get("details_submitted", False)

        logger.info(
            "Conta Stripe atualizada: %s | charges: %s, payouts: %s, details: %s",
            account_id,
            charges_enabled,
            payouts_enabled,
            details_submitted,
        )

        return {
            "account_id": account_id,
            "charges_enabled": charges_enabled,
            "payouts_enabled": payouts_enabled,
            "details_submitted": details_submitted,
        }
