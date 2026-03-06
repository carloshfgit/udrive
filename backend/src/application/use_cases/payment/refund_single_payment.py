"""
Refund Single Payment Use Case

Caso de uso para reembolso seletivo de um único Payment em checkout multi-item.
Permite que o admin reembolse apenas 1 aula do grupo, mantendo as demais
com status COMPLETED e seus agendamentos ativos.
"""

import structlog
from dataclasses import dataclass
from datetime import datetime, timezone

from src.application.dtos.payment_dtos import (
    RefundSinglePaymentDTO,
    RefundSinglePaymentResultDTO,
)
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    PaymentNotFoundException,
    RefundException,
    SchedulingNotFoundException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.infrastructure.services.token_encryption import decrypt_token

logger = structlog.get_logger()


@dataclass
class RefundSinglePaymentUseCase:
    """
    Caso de uso para reembolso seletivo (admin) de um único Payment.

    Diferente de ProcessRefundUseCase (cancelamento com regra de antecedência),
    este use case:
      - Grava mp_refund_id (vínculo direto com o reembolso no MP)
      - Cancela o Scheduling correspondente
      - Suporta reembolso parcial por porcentagem (default: 100%)
      - Garante idempotência: se já possui mp_refund_id, rejeita

    Fluxo:
        1. Buscar Payment por payment_id
        2. Validar: status COMPLETED, sem mp_refund_id, com gateway_payment_id
        3. Buscar InstructorProfile → obter access_token
        4. Calcular valor de reembolso (payment.amount * refund_percentage / 100)
        5. Chamar gateway.process_refund() → receber RefundResult
        6. Atualizar Payment (mp_refund_id, status, refund_amount, refunded_at)
        7. Persistir Payment
        8. Criar Transaction de reembolso
        9. Cancelar Scheduling correspondente
        10. Retornar RefundSinglePaymentResultDTO
    """

    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
    scheduling_repository: ISchedulingRepository
    payment_gateway: IPaymentGateway

    async def execute(
        self, dto: RefundSinglePaymentDTO
    ) -> RefundSinglePaymentResultDTO:
        """
        Executa o reembolso seletivo de um único Payment.

        Args:
            dto: Dados do reembolso (payment_id, admin_id, refund_percentage, reason).

        Returns:
            RefundSinglePaymentResultDTO com dados do reembolso e scheduling.

        Raises:
            PaymentNotFoundException: Se o pagamento não existir.
            RefundException: Se não puder ser reembolsado ou falhar no gateway.
            SchedulingNotFoundException: Se o scheduling não existir.
        """
        # 1. Buscar Payment
        payment = await self.payment_repository.get_by_id(dto.payment_id)
        if payment is None:
            raise PaymentNotFoundException(str(dto.payment_id))

        # 2. Validações
        if not payment.can_refund():
            raise RefundException(
                f"Pagamento não pode ser reembolsado. Status atual: {payment.status}"
            )

        if payment.mp_refund_id is not None:
            raise RefundException(
                f"Pagamento já possui reembolso vinculado (mp_refund_id: {payment.mp_refund_id})"
            )

        if payment.gateway_payment_id is None:
            raise RefundException("Pagamento não possui ID do gateway")

        # 3. Obter access_token do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            payment.instructor_id
        )
        if instructor_profile is None or not instructor_profile.has_mp_account:
            raise RefundException(
                f"Instrutor {payment.instructor_id} sem conta Mercado Pago vinculada"
            )

        # 4. Calcular valor de reembolso e atualizar entidade
        try:
            refund_amount = payment.process_refund(dto.refund_percentage)
        except ValueError as e:
            raise RefundException(str(e)) from e

        # 5. Chamar gateway para reembolso (API do Mercado Pago)
        try:
            refund_result = await self.payment_gateway.process_refund(
                payment_id=payment.gateway_payment_id,
                access_token=decrypt_token(instructor_profile.mp_access_token),
                amount=refund_amount,
            )
        except Exception as e:
            raise RefundException(
                f"Falha ao processar reembolso no Mercado Pago: {e}"
            ) from e

        # 6. Gravar mp_refund_id no Payment
        payment.mp_refund_id = refund_result.refund_id

        logger.info(
            "refund_single_payment_success",
            payment_id=str(payment.id),
            mp_refund_id=refund_result.refund_id,
            refund_amount=str(refund_amount),
            refund_percentage=dto.refund_percentage,
            admin_id=str(dto.admin_id),
        )

        # 7. Persistir Payment
        await self.payment_repository.update(payment)

        # 8. Criar Transaction de reembolso
        transaction = Transaction.create_refund_transaction(
            payment_id=payment.id,
            student_id=payment.student_id,
            amount=refund_amount,
            gateway_reference_id=refund_result.refund_id,
        )
        await self.transaction_repository.create(transaction)

        # 9. Cancelar Scheduling correspondente
        scheduling = await self.scheduling_repository.get_by_id(
            payment.scheduling_id
        )
        if scheduling is None:
            raise SchedulingNotFoundException(str(payment.scheduling_id))

        reason = dto.reason or "Reembolso administrativo"
        if scheduling.can_cancel():
            scheduling.cancel(cancelled_by=dto.admin_id, reason=reason)
        elif scheduling.is_disputed:
            scheduling.resolve_dispute_favor_student()
        else:
            logger.warning(
                "scheduling_cannot_be_cancelled",
                scheduling_id=str(scheduling.id),
                current_status=scheduling.status.value,
            )

        await self.scheduling_repository.update(scheduling)

        # 10. Retornar resultado
        return RefundSinglePaymentResultDTO(
            payment_id=payment.id,
            mp_refund_id=refund_result.refund_id,
            refund_amount=refund_amount,
            payment_status=payment.status.value,
            scheduling_id=scheduling.id,
            scheduling_status=scheduling.status.value,
        )
