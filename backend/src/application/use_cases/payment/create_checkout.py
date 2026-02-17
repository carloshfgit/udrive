"""
Create Checkout Use Case

Caso de uso para criar checkout do Mercado Pago (Checkout Pro).
Orquestra a criação de preferência de pagamento e retorna a URL
para o aluno ser redirecionado ao Mercado Pago.
"""

from dataclasses import dataclass

from src.application.dtos.payment_dtos import CheckoutResponseDTO, CreateCheckoutDTO
from src.application.use_cases.payment.calculate_split import CalculateSplitUseCase
from src.domain.entities.payment import Payment
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    GatewayAccountNotConnectedException,
    PaymentAlreadyProcessedException,
    PaymentFailedException,
    SchedulingNotFoundException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_gateway import IPaymentGateway
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.infrastructure.services.token_encryption import decrypt_token
from src.domain.interfaces.transaction_repository import ITransactionRepository
from src.infrastructure.config import Settings


# Deep links para retorno do Checkout Pro
BACK_URLS = {
    "success": "godrive://payment/success",
    "failure": "godrive://payment/error",
    "pending": "godrive://payment/pending",
}


@dataclass
class CreateCheckoutUseCase:
    """
    Caso de uso para criar checkout via Mercado Pago Checkout Pro.

    Fluxo:
        1. Buscar agendamento e validar status (CONFIRMED)
        2. Verificar se já existe pagamento para este agendamento
        3. Verificar se instrutor tem conta MP vinculada
        4. Calcular split (comissão plataforma + valor instrutor)
        5. Criar Payment com status PENDING
        6. Chamar gateway.create_checkout() com dados completos
        7. Atualizar Payment com preference_id → status PROCESSING
        8. Criar Transaction do tipo PAYMENT
        9. Retornar CheckoutResponseDTO com checkout_url (init_point)
    """

    scheduling_repository: ISchedulingRepository
    payment_repository: IPaymentRepository
    transaction_repository: ITransactionRepository
    instructor_repository: IInstructorRepository
    payment_gateway: IPaymentGateway
    calculate_split_use_case: CalculateSplitUseCase
    settings: Settings

    async def execute(self, dto: CreateCheckoutDTO) -> CheckoutResponseDTO:
        """
        Executa a criação do checkout.

        Args:
            dto: Dados para criar o checkout.

        Returns:
            CheckoutResponseDTO com URL de pagamento.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            PaymentAlreadyProcessedException: Se já existe pagamento.
            GatewayAccountNotConnectedException: Se instrutor sem conta MP.
            PaymentFailedException: Se falha na criação da preferência.
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

        # 3. Verificar conta MP do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            scheduling.instructor_id
        )
        if instructor_profile is None or not instructor_profile.has_mp_account:
            raise GatewayAccountNotConnectedException(str(scheduling.instructor_id))

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

        # 6. Criar checkout no Mercado Pago
        try:
            # Montar dados do payer (melhora taxa de aprovação)
            payer = None
            if dto.student_email:
                payer = {"email": dto.student_email}

            # Montar notification_url
            base_url = self.settings.mp_redirect_uri.rsplit("/oauth", 1)[0]
            notification_url = f"{base_url}/webhooks/mercadopago"

            checkout_result = await self.payment_gateway.create_checkout(
                items=[
                    {
                        "id": f"AULA-{dto.scheduling_id}",
                        "title": "Aula de Direção - GoDrive",
                        "description": f"Aula de direção em {scheduling.scheduled_datetime.strftime('%d/%m/%Y às %H:%M')}",
                        "category_id": "services",
                        "quantity": 1,
                        "unit_price": scheduling.price,
                    }
                ],
                marketplace_fee=split_result.platform_fee_amount,
                seller_access_token=decrypt_token(instructor_profile.mp_access_token),
                back_urls=BACK_URLS,
                payer=payer,
                statement_descriptor="GODRIVE AULA",
                external_reference=str(dto.scheduling_id),
                metadata={
                    "scheduling_id": str(dto.scheduling_id),
                    "payment_id": str(saved_payment.id),
                    "student_id": str(dto.student_id),
                    "instructor_id": str(scheduling.instructor_id),
                },
                notification_url=notification_url,
            )
        except Exception as e:
            # Marca pagamento como falho se a criação da preferência falhar
            saved_payment.mark_failed()
            await self.payment_repository.update(saved_payment)
            raise PaymentFailedException(str(e)) from e

        # 7. Atualizar Payment com preference_id → status PROCESSING
        saved_payment.mark_processing(checkout_result.preference_id)
        saved_payment.gateway_preference_id = checkout_result.preference_id
        saved_payment = await self.payment_repository.update(saved_payment)

        # 8. Criar Transaction do tipo PAYMENT
        transaction = Transaction.create_payment_transaction(
            payment_id=saved_payment.id,
            student_id=dto.student_id,
            amount=scheduling.price,
            gateway_reference_id=checkout_result.preference_id,
        )
        await self.transaction_repository.create(transaction)

        # 9. Retornar URL de checkout
        return CheckoutResponseDTO(
            payment_id=saved_payment.id,
            preference_id=checkout_result.preference_id,
            checkout_url=checkout_result.checkout_url,
            sandbox_url=checkout_result.sandbox_url,
            status=saved_payment.status.value,
        )
