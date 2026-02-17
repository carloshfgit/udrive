"""
Handle Payment Webhook Use Case

Caso de uso para processar notificações de webhook do Mercado Pago.
Consulta o status real do pagamento via API e atualiza entidades
Payment e Scheduling conforme o resultado.
"""

import logging
from dataclasses import dataclass

from src.application.dtos.payment_dtos import WebhookNotificationDTO
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import WebhookProcessingException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.infrastructure.services.token_encryption import decrypt_token

logger = logging.getLogger(__name__)

# Mapeamento de status do Mercado Pago → PaymentStatus do domínio
MP_STATUS_MAP = {
    "approved": PaymentStatus.COMPLETED,
    "authorized": PaymentStatus.PROCESSING,
    "in_process": PaymentStatus.PROCESSING,
    "in_mediation": PaymentStatus.PROCESSING,
    "pending": PaymentStatus.PROCESSING,
    "rejected": PaymentStatus.FAILED,
    "cancelled": PaymentStatus.FAILED,
    "refunded": PaymentStatus.REFUNDED,
    "charged_back": PaymentStatus.REFUNDED,
}


@dataclass
class HandlePaymentWebhookUseCase:
    """
    Caso de uso para processar notificações assíncronas do Mercado Pago.

    Fluxo:
        1. Ignorar notificações que não sejam de pagamento
        2. Consultar status real via gateway.get_payment_status()
        3. Buscar Payment pelo external_reference (scheduling_id) ou gateway_payment_id
        4. Idempotência — se já está no status final, retornar sem efeitos
        5. Mapear status MP → PaymentStatus
        6. Atualizar Payment
        7. Criar Transaction se necessário
        8. Atualizar Scheduling (confirmar se approved, manter se pending)
    """

    payment_repository: IPaymentRepository
    scheduling_repository: ISchedulingRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
    payment_gateway: IPaymentGateway

    async def execute(self, dto: WebhookNotificationDTO) -> None:
        """
        Processa notificação de webhook.

        Args:
            dto: Dados da notificação do Mercado Pago.

        Raises:
            WebhookProcessingException: Se houver erro irrecuperável.
        """
        # 1. Filtrar — só processa notificações de pagamento
        if dto.notification_type != "payment":
            logger.info(
                "Webhook ignorado: tipo=%s action=%s",
                dto.notification_type,
                dto.action,
            )
            return

        mp_payment_id = dto.data_id
        logger.info("Processando webhook para pagamento MP: %s", mp_payment_id)

        # 2. Buscar Payment existente pelo gateway_payment_id
        payment = await self.payment_repository.get_by_gateway_payment_id(mp_payment_id)

        if payment is None:
            # Pode ser a primeira notificação — vamos precisar do access_token
            # do instrutor para consultar o pagamento, mas sem o Payment local
            # não temos como saber qual instrutor. Logar e ignorar.
            logger.warning(
                "Payment não encontrado para gateway_payment_id=%s. "
                "Tentando consultar via API do MP com token da plataforma.",
                mp_payment_id,
            )
            # Não lançar exceção — retornar 200 para o MP não reenviar
            return

        # 3. Buscar instrutor para obter access_token
        instructor_profile = await self.instructor_repository.get_by_user_id(
            payment.instructor_id
        )
        if instructor_profile is None or not instructor_profile.has_mp_account:
            logger.error(
                "Instrutor %s sem conta MP vinculada para pagamento %s",
                payment.instructor_id,
                payment.id,
            )
            raise WebhookProcessingException(
                f"Instrutor {payment.instructor_id} sem conta MP"
            )

        # 4. Consultar status real no Mercado Pago
        try:
            status_result = await self.payment_gateway.get_payment_status(
                payment_id=mp_payment_id,
                access_token=decrypt_token(instructor_profile.mp_access_token),
            )
        except Exception as e:
            logger.error(
                "Falha ao consultar status do pagamento %s no MP: %s",
                mp_payment_id,
                str(e),
            )
            raise WebhookProcessingException(
                f"Falha ao consultar status: {e}"
            ) from e

        # 5. Mapear status MP → PaymentStatus
        new_status = MP_STATUS_MAP.get(status_result.status)
        if new_status is None:
            logger.warning(
                "Status MP desconhecido: %s para pagamento %s",
                status_result.status,
                mp_payment_id,
            )
            return

        # 6. Idempotência — se já está no status esperado, retornar
        if payment.status == new_status:
            logger.info(
                "Payment %s já está com status %s. Ignorando.",
                payment.id,
                new_status.value,
            )
            return

        # 7. Atualizar Payment conforme o status
        logger.info(
            "Atualizando Payment %s: %s → %s (MP status: %s, detail: %s)",
            payment.id,
            payment.status.value,
            new_status.value,
            status_result.status,
            status_result.status_detail,
        )

        # Atualizar payer_email se disponível
        if status_result.payer_email:
            payment.payer_email = status_result.payer_email

        if new_status == PaymentStatus.COMPLETED:
            await self._handle_approved(payment, mp_payment_id)
        elif new_status == PaymentStatus.FAILED:
            await self._handle_rejected(payment)
        elif new_status == PaymentStatus.REFUNDED:
            await self._handle_refunded(payment)
        else:
            # PROCESSING — manter estado atual, só atualizar gateway_payment_id
            payment.gateway_payment_id = mp_payment_id
            await self.payment_repository.update(payment)

    async def _handle_approved(self, payment, mp_payment_id: str) -> None:
        """Trata pagamento aprovado: marca COMPLETED e confirma Scheduling."""
        try:
            payment.mark_completed(payment.gateway_preference_id)
        except ValueError:
            # Já foi marcado como completed (idempotência)
            logger.info("Payment %s já estava completed.", payment.id)
            return

        payment.gateway_payment_id = mp_payment_id
        await self.payment_repository.update(payment)

        # Criar transaction de conclusão
        transaction = Transaction.create_payment_transaction(
            payment_id=payment.id,
            student_id=payment.student_id,
            amount=payment.amount,
            gateway_reference_id=mp_payment_id,
        )
        await self.transaction_repository.create(transaction)

        # Confirmar Scheduling (se ainda estiver PENDING)
        scheduling = await self.scheduling_repository.get_by_id(payment.scheduling_id)
        if scheduling and scheduling.can_confirm:
            scheduling.confirm()
            await self.scheduling_repository.update(scheduling)
            logger.info(
                "Scheduling %s confirmado após pagamento aprovado.",
                scheduling.id,
            )

    async def _handle_rejected(self, payment) -> None:
        """Trata pagamento rejeitado: marca FAILED."""
        payment.mark_failed()
        await self.payment_repository.update(payment)
        logger.info("Payment %s marcado como FAILED.", payment.id)

    async def _handle_refunded(self, payment) -> None:
        """Trata reembolso: marca REFUNDED se possível."""
        if payment.can_refund():
            payment.process_refund(100)
            await self.payment_repository.update(payment)
            logger.info("Payment %s marcado como REFUNDED.", payment.id)
        else:
            logger.warning(
                "Payment %s não pode ser reembolsado (status: %s).",
                payment.id,
                payment.status.value,
            )
