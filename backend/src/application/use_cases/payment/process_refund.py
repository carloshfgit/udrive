"""
Process Refund Use Case

Caso de uso para processar reembolso conforme regras de cancelamento.
Utiliza a API do Mercado Pago via IPaymentGateway.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.application.dtos.payment_dtos import ProcessRefundDTO, RefundResultDTO
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    PaymentNotFoundException,
    RefundException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.infrastructure.services.token_encryption import decrypt_token


@dataclass
class ProcessRefundUseCase:
    """
    Caso de uso para processar reembolso.

    Fluxo:
        1. Buscar Payment por payment_id
        2. Validar se pode ser reembolsado (status COMPLETED)
        3. Obter access_token do instrutor para autorizar o reembolso no MP
        4. Calcular valor de reembolso baseado na porcentagem
        5. Chamar IPaymentGateway.process_refund (API do Mercado Pago)
        6. Atualizar Payment com refund_amount e status
        7. Criar Transaction do tipo REFUND
        8. Retornar RefundResultDTO

    Regras (PAYMENT_FLOW.md):
        - >= 48h antes da aula: 100% reembolso
        - entre 24h e 48h: 50% reembolso
        - < 24h: 0% sem reembolso
    """

    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
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

        # 4. Calcular valor de reembolso
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

        # 6. Atualizar Payment
        await self.payment_repository.update(payment)

        # 7. Criar Transaction do tipo REFUND
        transaction = Transaction.create_refund_transaction(
            payment_id=payment.id,
            student_id=payment.student_id,
            amount=refund_amount,
            gateway_reference_id=refund_result.refund_id,
        )
        await self.transaction_repository.create(transaction)

        # 8. Retornar resultado
        return RefundResultDTO(
            payment_id=payment.id,
            refund_amount=refund_amount,
            refund_percentage=dto.refund_percentage,
            status=payment.status.value,
            refunded_at=payment.refunded_at or datetime.now(timezone.utc),
        )
