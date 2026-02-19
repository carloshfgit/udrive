"""
Handle Payment Webhook Use Case

Caso de uso para processar notificações de webhook do Mercado Pago.
Consulta o status real do pagamento via API e atualiza entidades
Payment e Scheduling conforme o resultado.

Suporta checkout multi-item: usa preference_group_id para atualizar
todos os payments de um mesmo checkout.
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

    Suporta checkout multi-item: quando um pagamento é aprovado, todos os
    payments do mesmo preference_group_id são atualizados e seus schedulings
    confirmados.

    Fluxo:
        1. Ignorar notificações que não sejam de pagamento
        2. Consultar status real via gateway.get_payment_status()
        3. Buscar Payment pelo gateway_payment_id
        4. Buscar todos os payments do grupo (preference_group_id)
        5. Idempotência — se já está no status final, retornar sem efeitos
        6. Mapear status MP → PaymentStatus
        7. Atualizar todos os Payments do grupo
        8. Criar Transaction se necessário
        9. Atualizar Schedulings (confirmar se approved, manter se pending)
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
            logger.warning(
                "Payment não encontrado para gateway_payment_id=%s. "
                "Tentando consultar via API do MP com token da plataforma.",
                mp_payment_id,
            )
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

        # 6. Buscar todos os payments do grupo (multi-item)
        if payment.preference_group_id:
            group_payments = await self.payment_repository.get_by_preference_group_id(
                payment.preference_group_id
            )
        else:
            # Fallback para checkout single-item legado
            group_payments = [payment]

        # 7. Idempotência — se o primeiro já está no status esperado, retornar
        if all(p.status == new_status for p in group_payments):
            logger.info(
                "Todos os payments do grupo já estão com status %s. Ignorando.",
                new_status.value,
            )
            return

        # 8. Atualizar todos os Payments conforme o status
        logger.info(
            "Atualizando %d payments do grupo %s: → %s (MP status: %s, detail: %s)",
            len(group_payments),
            payment.preference_group_id,
            new_status.value,
            status_result.status,
            status_result.status_detail,
        )

        # Atualizar payer_email se disponível (apenas no primeiro)
        if status_result.payer_email:
            for p in group_payments:
                p.payer_email = status_result.payer_email

        if new_status == PaymentStatus.COMPLETED:
            await self._handle_approved(group_payments, mp_payment_id)
        elif new_status == PaymentStatus.FAILED:
            await self._handle_rejected(group_payments)
        elif new_status == PaymentStatus.REFUNDED:
            await self._handle_refunded(group_payments)
        else:
            # PROCESSING — manter estado atual, só atualizar gateway_payment_id
            for p in group_payments:
                p.gateway_payment_id = mp_payment_id
                await self.payment_repository.update(p)

    async def _handle_approved(self, payments: list, mp_payment_id: str) -> None:
        """Trata pagamento aprovado: marca COMPLETED e confirma Schedulings."""
        for payment in payments:
            if payment.status == PaymentStatus.COMPLETED:
                continue  # Idempotência

            try:
                payment.mark_completed(payment.gateway_preference_id)
            except ValueError:
                logger.info("Payment %s já estava completed.", payment.id)
                continue

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

            # Confirmar Scheduling
            scheduling = await self.scheduling_repository.get_by_id(payment.scheduling_id)
            if scheduling and scheduling.can_confirm:
                scheduling.confirm()
                await self.scheduling_repository.update(scheduling)
                logger.info(
                    "Scheduling %s confirmado após pagamento aprovado.",
                    scheduling.id,
                )

    async def _handle_rejected(self, payments: list) -> None:
        """Trata pagamento rejeitado: marca FAILED para todos."""
        for payment in payments:
            if payment.status == PaymentStatus.FAILED:
                continue
            payment.mark_failed()
            await self.payment_repository.update(payment)
            logger.info("Payment %s marcado como FAILED.", payment.id)

    async def _handle_refunded(self, payments: list) -> None:
        """Trata reembolso: marca REFUNDED se possível para todos."""
        for payment in payments:
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
