"""
Process Payment Use Case

Caso de uso para processar pagamento de agendamento com split atômico.
"""

from dataclasses import dataclass

from src.application.dtos.payment_dtos import PaymentResponseDTO, ProcessPaymentDTO
from src.application.use_cases.payment.calculate_split import CalculateSplitUseCase
from src.domain.entities.payment import Payment
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    PaymentAlreadyProcessedException,
    PaymentFailedException,
    SchedulingNotFoundException,
    StripeAccountNotConnectedException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class ProcessPaymentUseCase:
    """
    Caso de uso para processar pagamento de aula.

    Fluxo:
        1. Buscar agendamento e validar status (CONFIRMED)
        2. Verificar se já existe pagamento para este agendamento
        3. Verificar se instrutor tem conta Stripe conectada
        4. Calcular split (usar CalculateSplitUseCase)
        5. Criar Payment com status PENDING
        6. Chamar IPaymentGateway.create_payment_intent com transfer_data
        7. Atualizar Payment com stripe_payment_intent_id
        8. Criar Transaction do tipo PAYMENT
        9. Retornar PaymentResponseDTO

    Regras de negócio (DEV_PLAN.md):
        - Split atômico no Stripe (transfer_data ao criar PaymentIntent)
        - Não acumular saldo na plataforma
    """

    scheduling_repository: ISchedulingRepository
    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
    user_repository: IUserRepository
    payment_gateway: IPaymentGateway
    calculate_split_use_case: CalculateSplitUseCase

    async def execute(self, dto: ProcessPaymentDTO) -> PaymentResponseDTO:
        """
        Executa o processamento do pagamento.

        Args:
            dto: Dados do pagamento a processar.

        Returns:
            PaymentResponseDTO: Pagamento processado.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            PaymentAlreadyProcessedException: Se já existe pagamento.
            StripeAccountNotConnectedException: Se instrutor sem conta Stripe.
            PaymentFailedException: Se falhar no gateway.
        """
        # 1. Buscar e validar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Verificar se já existe pagamento
        existing_payment = await self.payment_repository.get_by_scheduling_id(
            dto.scheduling_id
        )
        if existing_payment is not None:
            raise PaymentAlreadyProcessedException()

        # 3. Verificar conta Stripe do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            scheduling.instructor_id
        )
        if instructor_profile is None or not instructor_profile.stripe_account_id:
            raise StripeAccountNotConnectedException(str(scheduling.instructor_id))

        # 4. Calcular split
        split_result = self.calculate_split_use_case.execute(scheduling.price)

        # 5. Criar Payment com status PENDING
        payment = Payment(
            scheduling_id=dto.scheduling_id,
            student_id=dto.student_id,
            instructor_id=scheduling.instructor_id,
            amount=scheduling.price,
            platform_fee_percentage=split_result.platform_fee_percentage,
            platform_fee_amount=split_result.platform_fee_amount,
            instructor_amount=split_result.instructor_amount,
        )

        saved_payment = await self.payment_repository.create(payment)

        # 6. Chamar gateway com split atômico
        try:
            payment_intent_result = await self.payment_gateway.create_payment_intent(
                amount=scheduling.price,
                currency="brl",
                instructor_stripe_account_id=instructor_profile.stripe_account_id,
                instructor_amount=split_result.instructor_amount,
                metadata={
                    "scheduling_id": str(dto.scheduling_id),
                    "payment_id": str(saved_payment.id),
                    "student_id": str(dto.student_id),
                    "instructor_id": str(scheduling.instructor_id),
                },
            )
        except Exception as e:
            # Marca pagamento como falho
            saved_payment.mark_failed()
            await self.payment_repository.update(saved_payment)
            raise PaymentFailedException(str(e)) from e

        # 7. Atualizar Payment com stripe_payment_intent_id
        saved_payment.mark_processing(payment_intent_result.payment_intent_id)
        saved_payment = await self.payment_repository.update(saved_payment)

        # 8. Criar Transaction do tipo PAYMENT
        transaction = Transaction.create_payment_transaction(
            payment_id=saved_payment.id,
            student_id=dto.student_id,
            amount=scheduling.price,
            stripe_reference_id=payment_intent_result.payment_intent_id,
        )
        await self.transaction_repository.create(transaction)

        # 9. Buscar nomes para enriquecer resposta
        student = await self.user_repository.get_by_id(dto.student_id)
        instructor = await self.user_repository.get_by_id(scheduling.instructor_id)

        return PaymentResponseDTO(
            id=saved_payment.id,
            scheduling_id=saved_payment.scheduling_id,
            student_id=saved_payment.student_id,
            instructor_id=saved_payment.instructor_id,
            amount=saved_payment.amount,
            platform_fee_amount=saved_payment.platform_fee_amount,
            instructor_amount=saved_payment.instructor_amount,
            status=saved_payment.status.value,
            stripe_payment_intent_id=saved_payment.stripe_payment_intent_id,
            created_at=saved_payment.created_at,
            student_name=student.full_name if student else None,
            instructor_name=instructor.full_name if instructor else None,
            scheduling_datetime=scheduling.scheduled_datetime,
        )
