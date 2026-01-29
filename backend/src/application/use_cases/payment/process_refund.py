"""
Process Refund Use Case

Caso de uso para processar reembolso conforme regras de cancelamento.
"""

from dataclasses import dataclass
from datetime import datetime

from src.application.dtos.payment_dtos import ProcessRefundDTO, RefundResultDTO
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    PaymentNotFoundException,
    RefundException,
)
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository


@dataclass
class ProcessRefundUseCase:
    """
    Caso de uso para processar reembolso.

    Fluxo:
        1. Buscar Payment por payment_id
        2. Validar se pode ser reembolsado (status COMPLETED)
        3. Calcular valor de reembolso baseado na porcentagem
        4. Chamar IPaymentGateway.process_refund
        5. Atualizar Payment com refund_amount e status
        6. Criar Transaction do tipo REFUND
        7. Retornar RefundResultDTO

    Regras (DEV_PLAN.md):
        - > 24h antes da aula: 100% reembolso
        - < 24h antes da aula: 50% reembolso (multa)
    """

    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    payment_gateway: IPaymentGateway

    async def execute(self, dto: ProcessRefundDTO) -> RefundResultDTO:
        """
        Executa o processamento do reembolso.

        Args:
            dto: Dados do reembolso a processar.

        Returns:
            RefundResultDTO: Resultado do reembolso.

        Raises:
            PaymentNotFoundException: Se pagamento não existir.
            RefundException: Se não puder ser reembolsado ou falhar no gateway.
        """
        # 1. Buscar Payment
        payment = await self.payment_repository.get_by_id(dto.payment_id)
        if payment is None:
            raise PaymentNotFoundException(str(dto.payment_id))

        # 2. Validar se pode ser reembolsado
        if not payment.can_refund():
            raise RefundException(
                f"Pagamento não pode ser reembolsado. Status: {payment.status}"
            )

        if payment.stripe_payment_intent_id is None:
            raise RefundException("Pagamento não possui ID do Stripe")

        # 3. Calcular valor de reembolso
        try:
            refund_amount = payment.process_refund(dto.refund_percentage)
        except ValueError as e:
            raise RefundException(str(e)) from e

        # 4. Chamar gateway para reembolso
        try:
            refund_result = await self.payment_gateway.process_refund(
                payment_intent_id=payment.stripe_payment_intent_id,
                amount=refund_amount,
                reason=dto.reason,
            )
        except Exception as e:
            raise RefundException(f"Falha ao processar reembolso no Stripe: {e}") from e

        # 5. Atualizar Payment
        await self.payment_repository.update(payment)

        # 6. Criar Transaction do tipo REFUND
        transaction = Transaction.create_refund_transaction(
            payment_id=payment.id,
            student_id=payment.student_id,
            amount=refund_amount,
            stripe_reference_id=refund_result.refund_id,
        )
        await self.transaction_repository.create(transaction)

        # 7. Retornar resultado
        return RefundResultDTO(
            payment_id=payment.id,
            refund_amount=refund_amount,
            refund_percentage=dto.refund_percentage,
            status=payment.status.value,
            refunded_at=payment.refunded_at or datetime.utcnow(),
        )
