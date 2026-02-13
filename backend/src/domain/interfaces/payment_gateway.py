"""
IPaymentGateway Interface

Interface abstrata para gateway de pagamento (Stripe).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class PaymentIntentResult:
    """
    Resultado da criação de um PaymentIntent.

    Attributes:
        payment_intent_id: ID do PaymentIntent no Stripe.
        client_secret: Client secret para confirmar pagamento no frontend.
        status: Status do PaymentIntent.
        transfer_id: ID do Transfer (se aplicável).
    """

    payment_intent_id: str
    client_secret: str
    status: str
    transfer_id: str | None = None


@dataclass
class RefundResult:
    """
    Resultado do processamento de reembolso.

    Attributes:
        refund_id: ID do Refund no Stripe.
        amount: Valor reembolsado.
        status: Status do reembolso.
    """

    refund_id: str
    amount: Decimal
    status: str


@dataclass
class ConnectedAccountResult:
    """
    Resultado da criação de conta conectada.

    Attributes:
        account_id: ID da conta no Stripe.
        onboarding_url: URL para completar onboarding.
    """

    account_id: str
    onboarding_url: str | None = None


@dataclass
class TransferResult:
    """
    Resultado da criação de um Transfer no Stripe.

    Attributes:
        transfer_id: ID do Transfer no Stripe.
        amount: Valor transferido.
        status: Status do transfer.
        destination: ID da conta destino.
    """

    transfer_id: str
    amount: Decimal
    status: str
    destination: str


class IPaymentGateway(ABC):
    """
    Interface abstrata para gateway de pagamento.

    Define operações de integração com Stripe para pagamentos,
    reembolsos e onboarding de instrutores.
    """

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: Decimal,
        currency: str,
        transfer_group: str | None = None,
        metadata: dict | None = None,
    ) -> PaymentIntentResult:
        """
        Cria um PaymentIntent (Separate Charges).

        O pagamento é cobrado na conta da plataforma. O Transfer para o
        instrutor será criado separadamente via create_transfer após
        confirmação de conclusão da aula.

        Args:
            amount: Valor total em BRL.
            currency: Código da moeda (ex: 'brl').
            transfer_group: Grupo de reconciliação (vincula charge ao transfer futuro).
            metadata: Metadados adicionais.

        Returns:
            PaymentIntentResult com IDs e client_secret.
        """
        ...

    @abstractmethod
    async def create_transfer(
        self,
        amount: Decimal,
        destination_account_id: str,
        transfer_group: str | None = None,
        metadata: dict | None = None,
    ) -> TransferResult:
        """
        Cria um Transfer para a conta conectada do instrutor.

        Usado após a confirmação de conclusão da aula para liberar
        o pagamento retido em custódia.

        Args:
            amount: Valor a transferir em BRL.
            destination_account_id: ID da conta Stripe do instrutor.
            transfer_group: Grupo de reconciliação.
            metadata: Metadados adicionais.

        Returns:
            TransferResult com ID e status do transfer.
        """
        ...

    @abstractmethod
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
    ) -> PaymentIntentResult:
        """
        Confirma um PaymentIntent.

        Args:
            payment_intent_id: ID do PaymentIntent.

        Returns:
            PaymentIntentResult atualizado.
        """
        ...

    @abstractmethod
    async def process_refund(
        self,
        payment_intent_id: str,
        amount: Decimal,
        reason: str | None = None,
    ) -> RefundResult:
        """
        Processa reembolso de um pagamento.

        Args:
            payment_intent_id: ID do PaymentIntent original.
            amount: Valor a reembolsar em centavos.
            reason: Motivo do reembolso.

        Returns:
            RefundResult com status do reembolso.
        """
        ...

    @abstractmethod
    async def create_connected_account(
        self,
        email: str,
        instructor_id: UUID,
    ) -> ConnectedAccountResult:
        """
        Cria conta conectada para instrutor (Stripe Connect).

        Args:
            email: Email do instrutor.
            instructor_id: ID do instrutor no sistema.

        Returns:
            ConnectedAccountResult com ID da conta.
        """
        ...

    @abstractmethod
    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
    ) -> str:
        """
        Cria link de onboarding para conta conectada.

        Args:
            account_id: ID da conta Stripe.
            refresh_url: URL para refresh do link.
            return_url: URL de retorno após onboarding.

        Returns:
            URL de onboarding.
        """
        ...

    @abstractmethod
    async def get_account_status(
        self,
        account_id: str,
    ) -> dict:
        """
        Obtém status da conta conectada.

        Args:
            account_id: ID da conta Stripe.

        Returns:
            Dicionário com informações de status.
        """
        ...
