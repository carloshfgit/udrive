"""
MercadoPagoGateway Implementation

Implementação agnóstica do gateway usando as APIs do Mercado Pago.
"""

from decimal import Decimal
from typing import Any
import httpx
import structlog

logger = structlog.get_logger()

from src.domain.interfaces.payment_gateway import (
    IPaymentGateway,
    CheckoutResult,
    PaymentStatusResult,
    RefundResult,
    OAuthResult,
)
from src.infrastructure.config import Settings


class MercadoPagoGateway(IPaymentGateway):
    """
    Implementação do gateway de pagamento Mercado Pago.
    Usa httpx para chamadas diretas à API.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = "https://api.mercadopago.com"
        self.headers = {
            "Authorization": f"Bearer {settings.mp_access_token}",
            "Content-Type": "application/json",
        }

    async def create_checkout(
        self,
        items: list[dict],
        marketplace_fee: Decimal,
        seller_access_token: str,
        back_urls: dict[str, str],
        payer: dict[str, str | dict] | None = None,
        statement_descriptor: str | None = None,
        external_reference: str | None = None,
        metadata: dict | None = None,
        notification_url: str | None = None,
    ) -> CheckoutResult:
        """
        Cria uma preferência de checkout (Checkout Pro).

        Inclui todos os campos obrigatórios do Quality Checklist do MP:
        - items: id, title, description, category_id, quantity, unit_price
        - payer: email, first_name, last_name, identification, phone, address
        - statement_descriptor, back_urls, notification_url, external_reference
        """
        url = f"{self.base_url}/checkout/preferences"

        # Headers usam o access_token do vendedor para Split no Checkout Pro
        # conforme MP_INTEGRATION.md
        headers = {
            "Authorization": f"Bearer {seller_access_token}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "items": [
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "description": item.get("description", ""),
                    "category_id": item.get("category_id", "services"),
                    "quantity": item.get("quantity"),
                    "unit_price": float(item.get("unit_price")),
                    "currency_id": "BRL",
                }
                for item in items
            ],
            "marketplace_fee": float(marketplace_fee),
            "back_urls": back_urls,
            "auto_return": "all",
            "binary_mode": True,
        }

        # Campos opcionais — só incluir se preenchidos
        if payer:
            payload["payer"] = payer
        if statement_descriptor:
            payload["statement_descriptor"] = statement_descriptor
        if external_reference:
            payload["external_reference"] = external_reference
        if metadata:
            payload["metadata"] = metadata
        if notification_url:
            payload["notification_url"] = notification_url

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return CheckoutResult(
                preference_id=data["id"],
                checkout_url=data["init_point"],
                sandbox_url=data.get("sandbox_init_point"),
            )

    async def get_payment_status(
        self,
        payment_id: str,
        access_token: str,
    ) -> PaymentStatusResult:
        """
        Consulta o status de um pagamento.
        """
        url = f"{self.base_url}/v1/payments/{payment_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return PaymentStatusResult(
                payment_id=str(data["id"]),
                status=data["status"],
                status_detail=data["status_detail"],
                payer_email=data.get("payer", {}).get("email"),
            )

    async def get_merchant_order(
        self,
        merchant_order_id: str,
        access_token: str,
    ) -> dict[str, Any]:
        """
        Consulta detalhes de uma Merchant Order.
        Útil para extrair IDs de pagamento de webhooks do tipo merchant_order.
        """
        url = f"{self.base_url}/merchant_orders/{merchant_order_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def process_refund(
        self,
        payment_id: str,
        access_token: str,
        amount: Decimal | None = None,
    ) -> RefundResult:
        """
        Processa reembolso.
        """
        url = f"{self.base_url}/v1/payments/{payment_id}/refunds"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        payload = {}
        if amount:
            payload["amount"] = float(amount)

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return RefundResult(
                refund_id=str(data["id"]),
                amount=Decimal(str(data["amount"])),
                status=data["status"],
            )

    async def authorize_seller(
        self,
        authorization_code: str,
        redirect_uri: str,
    ) -> OAuthResult:
        """
        OAuth: Troca code por tokens.
        """
        url = f"{self.base_url}/oauth/token"
        
        payload = {
            "client_id": self.settings.mp_client_id,
            "client_secret": self.settings.mp_client_secret,
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": redirect_uri,
            "test_token": self.settings.environment == "development"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Logar o body do erro para facilitar diagnóstico
                logger.error(
                    "mp_oauth_error",
                    status_code=response.status_code,
                    response_body=response.text,
                    url=str(response.url)
                )
                raise e
            data = response.json()

            return OAuthResult(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_in=data["expires_in"],
                user_id=str(data["user_id"]),
                scope=data["scope"],
            )

    async def refresh_seller_token(
        self,
        refresh_token: str,
    ) -> OAuthResult:
        """
        OAuth: Renova token.
        """
        url = f"{self.base_url}/oauth/token"
        
        payload = {
            "client_id": self.settings.mp_client_id,
            "client_secret": self.settings.mp_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(
                    "mp_refresh_token_error",
                    status_code=response.status_code,
                    response_body=response.text,
                    url=str(response.url)
                )
                raise e
            data = response.json()

            return OAuthResult(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_in=data["expires_in"],
                user_id=str(data["user_id"]),
                scope=data["scope"],
            )
