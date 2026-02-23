"""
Handle Payment Webhook Use Case

Caso de uso para processar notificações de webhook do Mercado Pago.
Consulta o status real do pagamento via API e atualiza entidades
Payment e Scheduling conforme o resultado.

Suporta checkout multi-item: usa preference_group_id para atualizar
todos os payments de um mesmo checkout.
"""

import structlog
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

logger = structlog.get_logger()

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
        """
        # 1. Filtrar — processa notificações de pagamento e merchant_order
        if dto.notification_type not in ["payment", "merchant_order"]:
            logger.info(
                "webhook_ignored",
                type=dto.notification_type,
                action=dto.action,
            )
            return

        if dto.notification_type == "merchant_order":
            await self._handle_merchant_order(dto.data_id)
        else:
            await self._process_single_payment(dto.data_id)

    async def _handle_merchant_order(self, merchant_order_id: str) -> None:
        """Busca detalhes da merchant_order e processa seus pagamentos."""
        logger.info("merchant_order_processing", merchant_order_id=merchant_order_id)
        
        # 1. Buscar ordem via platform token para identificar o grupo
        try:
            # Usamos o token da plataforma (settings), não do instrutor aqui,
            # pois ainda não sabemos quem é o instrutor.
            from src.infrastructure.config import Settings
            settings = Settings()
            order_data = await self.payment_gateway.get_merchant_order(
                merchant_order_id, settings.mp_access_token
            )
        except Exception as e:
            logger.error(
                "merchant_order_fetch_error",
                merchant_order_id=merchant_order_id,
                error=str(e)
            )
            return

        external_reference = order_data.get("external_reference")
        if not external_reference:
            logger.warning("merchant_order_missing_external_reference", merchant_order_id=merchant_order_id)
            return

        # 2. Processar cada pagamento aprovado na ordem
        payments_in_order = order_data.get("payments", [])
        if not payments_in_order:
            logger.info("merchant_order_no_payments", merchant_order_id=merchant_order_id)
            return

        # Log diagnóstico para entender o estado dos pagamentos quando falha na UI
        logger.info(
            "merchant_order_payments_status",
            merchant_order_id=merchant_order_id,
            payments=payments_in_order
        )

        for mp_payment in payments_in_order:
            payment_id = str(mp_payment.get("id"))
            await self._process_single_payment(payment_id, preference_group_id=external_reference)

    async def _process_single_payment(self, mp_payment_id: str, preference_group_id: str | None = None) -> None:
        """Lógica original de processamento de um payment_id individual."""
        logger.info("single_payment_processing", mp_payment_id=mp_payment_id)

        # 2. Buscar Payment existente pelo gateway_payment_id
        payment = await self.payment_repository.get_by_gateway_payment_id(mp_payment_id)

        # Tentar fallback pela preference_group_id se recebida pela IPN
        if payment is None and preference_group_id:
            import uuid
            try:
                group_uuid = uuid.UUID(preference_group_id)
                group_payments = await self.payment_repository.get_by_preference_group_id(group_uuid)
                if group_payments:
                    # Todos do mesmo checkout compartilham o instrutor
                    payment = group_payments[0]
            except ValueError:
                pass

        if payment is None:
            # Tentar buscar por preference_id se o gateway_payment_id ainda for desconhecido
            # (isso acontece na primeira notificação de um pagamento novo)
            # Mas o get_payment_status nos dirá a preference_id.
            logger.warning(
                "payment_not_found_on_db",
                gateway_payment_id=mp_payment_id,
            )
            # Como não temos o payment, não sabemos o instructor_id para pegar o token.
            # Vamos tentar uma busca "cega" via API do MP usando o token da PLATAFORMA
            # para descobrir a qual preferencia esse pagamento pertence.
            try:
                from src.infrastructure.config import Settings
                settings = Settings()
                status_result = await self.payment_gateway.get_payment_status(
                    payment_id=mp_payment_id,
                    access_token=settings.mp_access_token,
                )
                
                # Buscar no DB pela preference_id (gateway_preference_id)
                # O MP retorna isso no payment detail se disponível
                # Se não, teremos que buscar por metadata ou external_reference se o status_result suportar
                logger.info("Consulta via platform token obteve status: %s", status_result.status)
                
                # Se o status_result não tem preference_id, vamos precisar buscar o payment
                # de outra forma. No GetPayment do MP tem.
                # Por enquanto, vamos assumir que o payment JÁ existe com gateway_preference_id
                # Vamos tentar buscar por gateway_preference_id no repositório
                # mas o DTO do gateway precisa retornar isso.
            except Exception as e:
                logger.error("payment_blind_search_failed", mp_payment_id=mp_payment_id, error=str(e))
                return
            
            # Se chegamos aqui sem o payment, temos um problema de rastreabilidade.
            return

        # 3. Buscar instrutor para obter access_token
        instructor_profile = await self.instructor_repository.get_by_user_id(
            payment.instructor_id
        )
        if instructor_profile is None or not instructor_profile.has_mp_account:
            logger.error(
                "instructor_missing_mp_account",
                instructor_id=payment.instructor_id,
                payment_id=payment.id,
            )
            raise WebhookProcessingException(
                f"Instrutor {payment.instructor_id} sem conta MP"
            )

        # 4. Consultar status real no Mercado Pago (usando token do vendedor)
        try:
            status_result = await self.payment_gateway.get_payment_status(
                payment_id=mp_payment_id,
                access_token=decrypt_token(instructor_profile.mp_access_token),
            )
        except Exception as e:
            logger.error(
                "mp_payment_status_fetch_error",
                mp_payment_id=mp_payment_id,
                error=str(e),
            )
            raise WebhookProcessingException(
                f"Falha ao consultar status: {e}"
            ) from e

        # 5. Mapear status MP → PaymentStatus
        new_status = MP_STATUS_MAP.get(status_result.status)
        if new_status is None:
            logger.warning(
                "mp_unknown_status",
                mp_status=status_result.status,
                mp_payment_id=mp_payment_id,
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
                "payment_group_already_at_target_status",
                status=new_status.value,
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
            if scheduling and scheduling.can_confirm():
                scheduling.confirm()
                await self.scheduling_repository.update(scheduling)
                logger.info(
                    "scheduling_confirmed_after_payment",
                    scheduling_id=scheduling.id,
                )

    async def _handle_rejected(self, payments: list) -> None:
        """Trata pagamento rejeitado: marca FAILED para todos."""
        for payment in payments:
            if payment.status == PaymentStatus.FAILED:
                continue
            payment.mark_failed()
            await self.payment_repository.update(payment)
            logger.info("payment_marked_failed", payment_id=payment.id)

    async def _handle_refunded(self, payments: list) -> None:
        """Trata reembolso: marca REFUNDED se possível para todos."""
        for payment in payments:
            if payment.can_refund():
                payment.process_refund(100)
                await self.payment_repository.update(payment)
                logger.info("payment_marked_refunded", payment_id=payment.id)
            else:
                logger.warning(
                    "payment_refund_not_allowed",
                    payment_id=payment.id,
                    status=payment.status.value,
                )
