"""
Stripe Payment Gateway Implementation

Implementação do gateway de pagamento usando a biblioteca oficial do Stripe.
"""

from decimal import Decimal

import stripe

from src.domain.interfaces.payment_gateway import (
    ConnectedAccountResult,
    IPaymentGateway,
    PaymentIntentResult,
    RefundResult,
)
from src.infrastructure.config import settings


class StripePaymentGateway(IPaymentGateway):
    """Implementação do gateway Stripe."""

    def __init__(self):
        # Inicializa com chave da configuração
        # Nota: Pode ser None se não configurado, métodos devem tratar isso
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def _ensure_configured(self):
        """Verifica se a chave API está configurada."""
        if not stripe.api_key:
            raise RuntimeError("Stripe API key not configured")

    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        instructor_stripe_account_id: str,
        instructor_amount: Decimal,
        metadata: dict[str, str] | None = None,
    ) -> PaymentIntentResult:
        self._ensure_configured()

        # Converter para centavos (int)
        amount_cents = int(amount * 100)
        instructor_amount_cents = int(instructor_amount * 100)

        # Criar PaymentIntent com transfer_data para split
        # Documentação: https://stripe.com/docs/connect/destination-charges
        try:
            intent = await stripe.PaymentIntent.create_async(
                amount=amount_cents,
                currency=currency.lower(),
                automatic_payment_methods={"enabled": True},
                metadata=metadata or {},
                transfer_data={
                    "destination": instructor_stripe_account_id,
                    "amount": instructor_amount_cents,
                },
            )

            return PaymentIntentResult(
                payment_intent_id=intent.id,
                client_secret=intent.client_secret,
                status=intent.status,
            )
        except stripe.StripeError as e:
            raise RuntimeError(f"Stripe Error: {str(e)}") from e

    async def process_refund(
        self, payment_intent_id: str, amount: Decimal | None = None, reason: str | None = None
    ) -> RefundResult:
        self._ensure_configured()

        try:
            # Se amount for None, é reembolso total
            amount_cents = int(amount * 100) if amount else None

            refund_params = {
                "payment_intent": payment_intent_id,
            }
            
            if amount_cents:
                refund_params["amount"] = amount_cents
                
            if reason:
                 # Stripe aceita: 'duplicate', 'fraudulent', 'requested_by_customer'
                 # Vamos mapear 'requested_by_customer' como default seguro se razão for livre
                 refund_params["reason"] = "requested_by_customer"
                 refund_params["metadata"] = {"original_reason": reason}

            refund = await stripe.Refund.create_async(**refund_params)

            return RefundResult(
                refund_id=refund.id,
                status=refund.status or "succeeded",
                amount_refunded=Decimal(refund.amount) / 100 if refund.amount else Decimal("0.00"),
            )
        except stripe.StripeError as e:
             raise RuntimeError(f"Stripe Refund Error: {str(e)}") from e

    async def create_connected_account(
        self, email: str, instructor_id: str
    ) -> ConnectedAccountResult:
        self._ensure_configured()

        try:
            # Cria conta Express para o instrutor
            account = await stripe.Account.create_async(
                type="express",
                country="BR",
                email=email,
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                metadata={"instructor_id": str(instructor_id)},
            )
            
            return ConnectedAccountResult(
                account_id=account.id,
                type=account.type,
                country=account.country,
                details_submitted=account.details_submitted,
            )
        except stripe.StripeError as e:
             raise RuntimeError(f"Stripe Account Error: {str(e)}") from e

    async def create_account_link(
        self, account_id: str, refresh_url: str, return_url: str
    ) -> str:
        self._ensure_configured()

        try:
            account_link = await stripe.AccountLink.create_async(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )
            return account_link.url
        except stripe.StripeError as e:
             raise RuntimeError(f"Stripe Account Link Error: {str(e)}") from e

    async def get_account_status(self, account_id: str) -> dict:
        self._ensure_configured()
        
        try:
            account = await stripe.Account.retrieve_async(account_id)
            return {
                "id": account.id,
                "details_submitted": account.details_submitted,
                "charges_enabled": account.charges_enabled,
                "payouts_enabled": account.payouts_enabled,
            }
        except stripe.StripeError as e:
             raise RuntimeError(f"Stripe Get Account Error: {str(e)}") from e
