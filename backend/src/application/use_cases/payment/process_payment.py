"""
Process Payment Use Case

Caso de uso para processar pagamento de agendamento com modelo de custódia.
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4
from src.application.dtos.payment_dtos import (
    CartPaymentResponseDTO,
    PaymentResponseDTO,
    ProcessPaymentDTO,
)
from src.infrastructure.config import settings
from src.application.use_cases.payment.calculate_split import CalculateSplitUseCase
from src.application.use_cases.payment.calculate_student_price import (
    CalculateStudentPriceUseCase,
)
from src.domain.entities.payment import Payment
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    DomainException,
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

    Fluxo (Separate Charges and Transfers — Escrow):
        1. Buscar agendamentos (múltiplos no carrinho) e validar status
        2. Verificar se já existe pagamento para cada um
        3. Verificar se cada instrutor tem conta Stripe conectada
        4. Calcular preço total all-inclusive para o aluno
        5. Criar registros Payment (PENDING) com transfer_group comum
        6. Chamar IPaymentGateway.create_payment_intent único para o total
        7. Atualizar Payments com stripe_payment_intent_id (status PROCESSING)
        8. Criar Transactions do tipo PAYMENT para cada item
        9. Retornar CartPaymentResponseDTO com client_secret único

    O pagamento ficará em PROCESSING até o webhook confirmar (→ HELD).
    A liberação para os instrutores ocorre pós-aula.
    """

    scheduling_repository: ISchedulingRepository
    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
    user_repository: IUserRepository
    payment_gateway: IPaymentGateway
    calculate_split_use_case: CalculateSplitUseCase
    calculate_student_price_use_case: CalculateStudentPriceUseCase

    async def execute(self, dto: ProcessPaymentDTO) -> CartPaymentResponseDTO:
        """
        Executa o processamento do pagamento para um ou mais agendamentos.

        Args:
            dto: Dados do pagamento a processar.

        Returns:
            CartPaymentResponseDTO: Resultado do checkout do carrinho.

        Raises:
            SchedulingNotFoundException: Se algum agendamento não existir.
            PaymentAlreadyProcessedException: Se já existe pagamento para algum item.
            StripeAccountNotConnectedException: Se algum instrutor sem conta Stripe.
            PaymentFailedException: Se falhar no gateway.
        """
        if not dto.scheduling_ids:
            raise DomainException("Lista de agendamentos não pode estar vazia")

        # 1 e 2. Buscar agendamentos e validar
        schedulings = []
        for s_id in dto.scheduling_ids:
            scheduling = await self.scheduling_repository.get_by_id(s_id)
            if scheduling is None:
                raise SchedulingNotFoundException(str(s_id))

            # Verificar se já existe pagamento
            existing_payment = await self.payment_repository.get_by_scheduling_id(s_id)
            if existing_payment is not None:
                # Se o pagamento anterior falhou, podemos tentar novamente
                # Mas se estiver pendente, ativo ou completo, não permitimos duplicidade
                if not existing_payment.is_failed:
                    raise PaymentAlreadyProcessedException(
                        f"Já existe um pagamento ativo para o agendamento {s_id}"
                    )

            # Verificar conta Stripe do instrutor
            instr_profile = await self.instructor_repository.get_by_user_id(
                scheduling.instructor_id
            )
            if instr_profile is None or not instr_profile.stripe_account_id:
                raise StripeAccountNotConnectedException(str(scheduling.instructor_id))

            schedulings.append(scheduling)

        # 3. Calcular totais e preparar dados
        total_total_student_price = Decimal("0.00")
        payment_items_data = []
        cart_id = uuid4()
        transfer_group = f"cart_{cart_id}"

        for scheduling in schedulings:
            student_price = self.calculate_student_price_use_case.execute(
                instructor_rate=scheduling.price,
            )
            total_total_student_price += student_price.total_student_price
            payment_items_data.append((scheduling, student_price))

        # 4. Criar PaymentIntent único para o total do carrinho
        try:
            payment_intent_result = await self.payment_gateway.create_payment_intent(
                amount=total_total_student_price,
                currency="brl",
                transfer_group=transfer_group,
                metadata={
                    "cart_id": str(cart_id),
                    "student_id": str(dto.student_id),
                    "scheduling_ids": ",".join([str(s.id) for s in schedulings]),
                    "checkout_type": "cart",
                },
            )
        except Exception as e:
            raise PaymentFailedException(str(e)) from e

        # 5. Criar registros de Payment e Transaction para cada item do carrinho
        payment_responses = []
        for scheduling, student_price in payment_items_data:
            payment = Payment(
                scheduling_id=scheduling.id,
                student_id=dto.student_id,
                instructor_id=scheduling.instructor_id,
                amount=student_price.total_student_price,
                platform_fee_percentage=Decimal(str(settings.platform_fee_percentage)),
                platform_fee_amount=student_price.platform_fee_amount,
                instructor_amount=scheduling.price,
                stripe_fee_amount=student_price.stripe_fee_estimate,
                total_student_amount=student_price.total_student_price,
            )
            payment.transfer_group = transfer_group
            payment.mark_processing(payment_intent_result.payment_intent_id)

            saved_payment = await self.payment_repository.create(payment)

            # Criar Transaction
            transaction = Transaction.create_payment_transaction(
                payment_id=saved_payment.id,
                student_id=dto.student_id,
                amount=student_price.total_student_price,
                stripe_reference_id=payment_intent_result.payment_intent_id,
            )
            await self.transaction_repository.create(transaction)

            # Buscar nomes para enriquecer resposta (opcional, mas bom manter)
            student = await self.user_repository.get_by_id(dto.student_id)
            instructor = await self.user_repository.get_by_id(scheduling.instructor_id)

            payment_responses.append(
                PaymentResponseDTO(
                    id=saved_payment.id,
                    scheduling_id=saved_payment.scheduling_id,
                    student_id=saved_payment.student_id,
                    instructor_id=saved_payment.instructor_id,
                    amount=saved_payment.amount,
                    platform_fee_amount=saved_payment.platform_fee_amount,
                    instructor_amount=saved_payment.instructor_amount,
                    status=saved_payment.status.value,
                    stripe_payment_intent_id=saved_payment.stripe_payment_intent_id,
                    stripe_fee_amount=saved_payment.stripe_fee_amount,
                    total_student_amount=saved_payment.total_student_amount,
                    client_secret=payment_intent_result.client_secret,
                    transfer_group=saved_payment.transfer_group,
                    created_at=saved_payment.created_at,
                    student_name=student.full_name if student else None,
                    instructor_name=instructor.full_name if instructor else None,
                    scheduling_datetime=scheduling.scheduled_datetime,
                )
            )

        return CartPaymentResponseDTO(
            payments=payment_responses,
            transfer_group=transfer_group,
            total_amount=total_total_student_price,
            client_secret=payment_intent_result.client_secret,
        )
