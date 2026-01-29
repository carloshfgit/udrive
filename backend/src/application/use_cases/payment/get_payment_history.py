"""
Get Payment History Use Case

Caso de uso para obter histórico financeiro do usuário.
"""

from dataclasses import dataclass

from src.application.dtos.payment_dtos import (
    GetPaymentHistoryDTO,
    PaymentHistoryResponseDTO,
    PaymentResponseDTO,
)
from src.domain.entities.user_type import UserType
from src.domain.exceptions import UserNotFoundException
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class GetPaymentHistoryUseCase:
    """
    Caso de uso para obter histórico de pagamentos.

    Fluxo:
        1. Determinar tipo de usuário (aluno ou instrutor)
        2. Buscar pagamentos via IPaymentRepository
        3. Enriquecer com dados adicionais
        4. Retornar PaymentHistoryResponseDTO paginado
    """

    user_repository: IUserRepository
    payment_repository: IPaymentRepository
    scheduling_repository: ISchedulingRepository

    async def execute(self, dto: GetPaymentHistoryDTO) -> PaymentHistoryResponseDTO:
        """
        Executa a busca do histórico de pagamentos.

        Args:
            dto: Dados da consulta.

        Returns:
            PaymentHistoryResponseDTO: Histórico paginado.

        Raises:
            UserNotFoundException: Se usuário não existir.
        """
        # 1. Buscar usuário e determinar tipo
        user = await self.user_repository.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundException(str(dto.user_id))

        # 2. Buscar pagamentos baseado no tipo de usuário
        if user.user_type == UserType.STUDENT:
            payments = await self.payment_repository.list_by_student(
                student_id=dto.user_id,
                limit=dto.limit,
                offset=dto.offset,
            )
            total_count = await self.payment_repository.count_by_student(dto.user_id)
        else:
            payments = await self.payment_repository.list_by_instructor(
                instructor_id=dto.user_id,
                limit=dto.limit,
                offset=dto.offset,
            )
            total_count = await self.payment_repository.count_by_instructor(dto.user_id)

        # 3. Converter para DTOs e enriquecer
        payment_dtos: list[PaymentResponseDTO] = []
        for payment in payments:
            scheduling = await self.scheduling_repository.get_by_id(
                payment.scheduling_id
            )
            scheduling_datetime = (
                scheduling.scheduled_datetime if scheduling else None
            )

            payment_dtos.append(
                PaymentResponseDTO(
                    id=payment.id,
                    scheduling_id=payment.scheduling_id,
                    student_id=payment.student_id,
                    instructor_id=payment.instructor_id,
                    amount=payment.amount,
                    platform_fee_amount=payment.platform_fee_amount,
                    instructor_amount=payment.instructor_amount,
                    status=payment.status.value,
                    stripe_payment_intent_id=payment.stripe_payment_intent_id,
                    refund_amount=payment.refund_amount,
                    refunded_at=payment.refunded_at,
                    created_at=payment.created_at,
                    scheduling_datetime=scheduling_datetime,
                )
            )

        # 4. Retornar resultado paginado
        return PaymentHistoryResponseDTO(
            payments=payment_dtos,
            total_count=total_count,
            limit=dto.limit,
            offset=dto.offset,
            has_more=(dto.offset + len(payments)) < total_count,
        )
