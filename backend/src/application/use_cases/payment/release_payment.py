"""
Release Payment Use Case

Caso de uso para liberar o pagamento retido em custódia (escrow)
e transferir o valor ao instrutor após confirmação de conclusão da aula.
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    PaymentNotFoundException,
    PaymentNotHeldException,
    StripeAccountNotConnectedException,
    DomainException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository

logger = logging.getLogger(__name__)


@dataclass
class ReleasePaymentUseCase:
    """
    Caso de uso para liberar pagamento retido em custódia.

    Fluxo:
        1. Buscar Payment pelo scheduling_id
        2. Validar que está em status HELD
        3. Buscar conta Stripe do instrutor
        4. Criar Transfer via gateway (Separate Charges and Transfers)
        5. Marcar Payment como COMPLETED com stripe_transfer_id
        6. Criar Transaction de tipo INSTRUCTOR_PAYOUT
        7. Salvar

    Chamado por:
        - CompleteSchedulingUseCase (confirmação do aluno)
        - Task automatizada de auto-confirmação (24h após término)
    """

    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    payment_gateway: IPaymentGateway
    instructor_repository: IInstructorRepository

    async def execute(self, scheduling_id: UUID) -> None:
        """
        Executa a liberação do pagamento ao instrutor.

        Args:
            scheduling_id: ID do agendamento cuja aula foi concluída.

        Raises:
            PaymentNotFoundException: Se não existe payment para o scheduling.
            PaymentNotHeldException: Se o payment não está em custódia.
            StripeAccountNotConnectedException: Se instrutor sem conta Stripe.
            RuntimeError: Se o Transfer falhar no Stripe.
        """
        # 1. Buscar Payment pelo scheduling_id
        payment = await self.payment_repository.get_by_scheduling_id(scheduling_id)
        if payment is None:
            raise PaymentNotFoundException(str(scheduling_id))

        # 2. Validar status HELD
        if payment.status == "disputed": # Explicit check for safety
            raise DomainException(f"Pagamento {payment.id} está em disputa e não pode ser liberado.")
            
        if not payment.is_held:
            raise PaymentNotHeldException(str(payment.id))

        # 3. Buscar conta Stripe do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            payment.instructor_id
        )
        if instructor_profile is None or not instructor_profile.stripe_account_id:
            raise StripeAccountNotConnectedException(str(payment.instructor_id))

        # 4. Criar Transfer via gateway
        transfer_result = await self.payment_gateway.create_transfer(
            amount=payment.instructor_amount,
            destination_account_id=instructor_profile.stripe_account_id,
            transfer_group=payment.transfer_group,
            metadata={
                "payment_id": str(payment.id),
                "scheduling_id": str(scheduling_id),
                "instructor_id": str(payment.instructor_id),
            },
        )

        # 5. Marcar Payment como COMPLETED
        payment.mark_completed(stripe_transfer_id=transfer_result.transfer_id)
        await self.payment_repository.update(payment)

        # 6. Criar Transaction de tipo INSTRUCTOR_PAYOUT
        transaction = Transaction.create_instructor_payout_transaction(
            payment_id=payment.id,
            instructor_id=payment.instructor_id,
            amount=payment.instructor_amount,
            stripe_reference_id=transfer_result.transfer_id,
        )
        await self.transaction_repository.create(transaction)

        logger.info(
            "Pagamento %s liberado para instrutor %s. Transfer: %s",
            payment.id,
            payment.instructor_id,
            transfer_result.transfer_id,
        )
