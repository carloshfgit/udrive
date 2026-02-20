"""
Create Checkout Use Case

Caso de uso para criar checkout do Mercado Pago (Checkout Pro).
Suporta checkout multi-item: múltiplos agendamentos em uma única preferência.
"""

from decimal import Decimal
from dataclasses import dataclass
from uuid import uuid4

import structlog

from src.application.dtos.payment_dtos import CheckoutResponseDTO, CreateCheckoutDTO
from src.application.use_cases.payment.calculate_split import CalculateSplitUseCase
from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.transaction import Transaction
from src.domain.exceptions import (
    GatewayAccountNotConnectedException,
    MixedInstructorsException,
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

logger = structlog.get_logger()

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

    Suporta checkout multi-item: múltiplos agendamentos de um mesmo
    instrutor em uma única preferência de pagamento.

    Fluxo:
        1. Buscar todos os agendamentos e validar
        2. Verificar que todos pertencem ao mesmo instrutor
        3. Verificar se já existe pagamento para algum dos agendamentos
        4. Verificar se instrutor tem conta MP vinculada
        5. Calcular split para cada item
        6. Gerar preference_group_id e criar N Payments com status PENDING
        7. Chamar gateway.create_checkout() com lista de items
        8. Atualizar Payments com preference_id → status PROCESSING
        9. Criar Transaction do tipo PAYMENT
        10. Retornar CheckoutResponseDTO com checkout_url (init_point)
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
        Executa a criação do checkout multi-item.

        Args:
            dto: Dados para criar o checkout (scheduling_ids, student_id, etc).

        Returns:
            CheckoutResponseDTO com URL de pagamento.

        Raises:
            SchedulingNotFoundException: Se algum agendamento não existir.
            MixedInstructorsException: Se agendamentos de instrutores diferentes.
            PaymentAlreadyProcessedException: Se já existe pagamento.
            GatewayAccountNotConnectedException: Se instrutor sem conta MP.
            PaymentFailedException: Se falha na criação da preferência.
        """
        if not dto.scheduling_ids:
            raise SchedulingNotFoundException("Nenhum agendamento informado")

        # 1. Buscar e validar todos os agendamentos
        schedulings = []
        for sid in dto.scheduling_ids:
            scheduling = await self.scheduling_repository.get_by_id(sid)
            if scheduling is None:
                raise SchedulingNotFoundException(str(sid))
            if scheduling.is_cancelled:
                raise SchedulingNotFoundException(
                    f"Agendamento {sid} expirado ou cancelado"
                )
            schedulings.append(scheduling)

        # 2. Verificar que todos pertencem ao mesmo instrutor
        instructor_ids = {s.instructor_id for s in schedulings}
        if len(instructor_ids) > 1:
            raise MixedInstructorsException()
        instructor_id = instructor_ids.pop()

        # 3. Verificar se já existe pagamento para algum dos agendamentos
        existing_payments_map = {}
        for scheduling in schedulings:
            existing_payment = await self.payment_repository.get_by_scheduling_id(
                scheduling.id
            )
            if existing_payment is not None:
                if existing_payment.status == PaymentStatus.COMPLETED:
                    raise PaymentAlreadyProcessedException()
                existing_payments_map[scheduling.id] = existing_payment

        # 4. Verificar conta MP do instrutor
        instructor_profile = await self.instructor_repository.get_by_user_id(
            instructor_id
        )
        if instructor_profile is None or not instructor_profile.has_mp_account:
            raise GatewayAccountNotConnectedException(str(instructor_id))

        # 5. Calcular split para cada item e gerar preference_group_id
        preference_group_id = uuid4()
        saved_payments: list[Payment] = []
        items: list[dict] = []
        total_marketplace_fee = Decimal("0.00")
        total_amount = Decimal("0.00")

        for scheduling in schedulings:
            # Recalcular valor base conforme perfil atual
            hours = Decimal(scheduling.duration_minutes) / Decimal(60)
            instructor_base_amount = instructor_profile.hourly_rate * hours

            split_result = self.calculate_split_use_case.execute(
                scheduling.price, instructor_base_amount=instructor_base_amount
            )

            # 6. Criar ou atualizar Payment com status PENDING
            existing_payment = existing_payments_map.get(scheduling.id)
            if existing_payment:
                existing_payment.amount = scheduling.price
                existing_payment.platform_fee_percentage = split_result.platform_fee_percentage
                existing_payment.platform_fee_amount = split_result.platform_fee_amount
                existing_payment.instructor_amount = split_result.instructor_amount
                existing_payment.preference_group_id = preference_group_id
                existing_payment.status = PaymentStatus.PENDING
                saved_payment = await self.payment_repository.update(existing_payment)
            else:
                payment = Payment(
                    scheduling_id=scheduling.id,
                    student_id=dto.student_id,
                    instructor_id=instructor_id,
                    amount=scheduling.price,
                    platform_fee_percentage=split_result.platform_fee_percentage,
                    platform_fee_amount=split_result.platform_fee_amount,
                    instructor_amount=split_result.instructor_amount,
                    preference_group_id=preference_group_id,
                )
                saved_payment = await self.payment_repository.create(payment)
            saved_payments.append(saved_payment)

            # Montar item para MP
            items.append({
                "id": f"AULA-{scheduling.id}",
                "title": "Aula de Direção - GoDrive",
                "description": f"Aula de direção em {scheduling.scheduled_datetime.strftime('%d/%m/%Y às %H:%M')}",
                "category_id": "services",
                "quantity": 1,
                "unit_price": scheduling.price,
            })

            total_marketplace_fee += split_result.platform_fee_amount
            total_amount += scheduling.price

        # 7. Criar checkout no Mercado Pago
        try:
            payer = None
            if dto.student_email:
                payer = {"email": dto.student_email}

            base_url = self.settings.mp_redirect_uri.rsplit("/oauth", 1)[0]
            notification_url = f"{base_url}/shared/webhooks/mercadopago"

            checkout_result = await self.payment_gateway.create_checkout(
                items=items,
                marketplace_fee=total_marketplace_fee,
                seller_access_token=decrypt_token(instructor_profile.mp_access_token),
                back_urls=BACK_URLS,
                payer=payer,
                statement_descriptor="GODRIVE AULA",
                external_reference=str(preference_group_id),
                metadata={
                    "preference_group_id": str(preference_group_id),
                    "scheduling_ids": [str(s.id) for s in schedulings],
                    "payment_ids": [str(p.id) for p in saved_payments],
                    "student_id": str(dto.student_id),
                    "instructor_id": str(instructor_id),
                },
                notification_url=notification_url,
            )
        except Exception as e:
            # Marca todos os pagamentos como falhos
            for p in saved_payments:
                p.mark_failed()
                await self.payment_repository.update(p)
            raise PaymentFailedException(str(e)) from e

        # 8. Atualizar Payments com preference_id → status PROCESSING
        first_payment = saved_payments[0]
        for p in saved_payments:
            p.mark_processing(checkout_result.preference_id)
            p.gateway_preference_id = checkout_result.preference_id
            await self.payment_repository.update(p)

        # 9. (Removido: Transaction será criada apenas no webhook quando aprovado)

        logger.info(
            "multi_item_checkout_created",
            preference_group_id=str(preference_group_id),
            num_items=len(schedulings),
            total_amount=str(total_amount),
            total_marketplace_fee=str(total_marketplace_fee),
        )

        # 10. Retornar URL de checkout
        return CheckoutResponseDTO(
            payment_id=first_payment.id,
            preference_id=checkout_result.preference_id,
            checkout_url=checkout_result.checkout_url,
            sandbox_url=checkout_result.sandbox_url,
            status=first_payment.status.value,
        )
