"""
IPaymentGateway Interface

Interface abstrata para gateway de pagamento agnóstico.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CheckoutResult:
    """
    Resultado da criação de um checkout.

    Attributes:
        preference_id: ID da preferência/sessão no gateway.
        checkout_url: URL para redirecionar o usuário para o pagamento.
        sandbox_url: URL de teste (opcional).
    """

    preference_id: str
    checkout_url: str
    sandbox_url: str | None = None


@dataclass
class PaymentStatusResult:
    """
    Resultado da consulta de status de pagamento.

    Attributes:
        payment_id: ID do pagamento no gateway.
        status: Status resumido (approved, pending, rejected, etc).
        status_detail: Detalhes do status.
        payer_email: Email do pagador.
    """

    payment_id: str
    status: str
    status_detail: str
    payer_email: str | None = None


@dataclass
class RefundResult:
    """
    Resultado do processamento de reembolso.

    Attributes:
        refund_id: ID do reembolso no gateway.
        amount: Valor reembolsado.
        status: Status do reembolso (succeeded, pending, etc).
    """

    refund_id: str
    amount: Decimal
    status: str


@dataclass
class OAuthResult:
    """
    Resultado da autorização OAuth de um vendedor.

    Attributes:
        access_token: Token de acesso do vendedor.
        refresh_token: Token de renovação.
        expires_in: Segundos para expiração.
        user_id: ID do usuário no gateway.
        scope: Escopo de permissões.
    """

    access_token: str
    refresh_token: str
    expires_in: int
    user_id: str
    scope: str


class IPaymentGateway(ABC):
    """
    Interface abstrata para gateway de pagamento.

    Define operações agnósticas para pagamentos, reembolsos
    e autorização de vendedores (OAuth).
    """

    @abstractmethod
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
        Cria uma preferência de checkout no gateway.

        Args:
            items: Lista de itens com campos obrigatórios do Quality Checklist:
                - id, title, description, category_id, quantity, unit_price.
            marketplace_fee: Valor da comissão da plataforma.
            seller_access_token: Token do vendedor (Split).
            back_urls: URLs de retorno (success, failure, pending).
            payer: Dados do pagador (email, first_name, last_name,
                identification, phone, address). Melhora taxa de aprovação.
            statement_descriptor: Descrição na fatura do cartão. Reduz
                contestações/chargebacks.
            external_reference: Referência externa para rastreamento.
            metadata: Metadados adicionais.
            notification_url: URL para receber webhooks.

        Returns:
            CheckoutResult com URL de redirecionamento.
        """
        ...

    @abstractmethod
    async def get_payment_status(
        self,
        payment_id: str,
        access_token: str,
    ) -> PaymentStatusResult:
        """
        Consulta o status de um pagamento.

        Args:
            payment_id: ID do pagamento no gateway.
            access_token: Token para autorizar a consulta.

        Returns:
            PaymentStatusResult with details of the status.
        """
        ...

    @abstractmethod
    async def get_merchant_order(
        self,
        merchant_order_id: str,
        access_token: str,
    ) -> dict:
        """
        Consult details of a Merchant Order.

        Args:
            merchant_order_id: ID of the order in the gateway.
            access_token: Token to authorize the query.

        Returns:
            Dict with order details.
        """
        ...

    @abstractmethod
    async def process_refund(
        self,
        payment_id: str,
        access_token: str,
        amount: Decimal | None = None,
    ) -> RefundResult:
        """
        Processa reembolso de um pagamento.

        Args:
            payment_id: ID do pagamento original.
            access_token: Token para autorizar o reembolso.
            amount: Valor a reembolsar (None para total).

        Returns:
            RefundResult com status do reembolso.
        """
        ...

    @abstractmethod
    async def authorize_seller(
        self,
        authorization_code: str,
        redirect_uri: str,
    ) -> OAuthResult:
        """
        Troca código de autorização por tokens (OAuth).

        Args:
            authorization_code: Código recebido no callback.
            redirect_uri: URI de redirecionamento usada no início.

        Returns:
            OAuthResult com tokens do vendedor.
        """
        ...

    @abstractmethod
    async def refresh_seller_token(
        self,
        refresh_token: str,
    ) -> OAuthResult:
        """
        Renova tokens expirados usando refresh_token.

        Args:
            refresh_token: Token de renovação.

        Returns:
            OAuthResult com novos tokens.
        """
        ...
