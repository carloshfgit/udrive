"""
Get Instructor Earnings Use Case

Caso de uso para obter os ganhos financeiros do instrutor.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.application.dtos.payment_dtos import InstructorEarningsDTO
from src.domain.entities.payment_status import PaymentStatus
from src.domain.exceptions import InstructorNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.payment_repository import IPaymentRepository


@dataclass
class GetInstructorEarningsUseCase:
    """
    Caso de uso para calcular ganhos do instrutor.

    Fluxo:
        1. Verificar se instrutor existe
        2. Buscar pagamentos do instrutor
        3. Calcular total de ganhos (pagamentos completados)
        4. Calcular ganhos pendentes (pagamentos processando ou pendentes)
        5. Contar aulas concluídas
    """

    instructor_repository: IInstructorRepository
    payment_repository: IPaymentRepository

    async def execute(self, instructor_id: str) -> InstructorEarningsDTO:
        """
        Executa o cálculo de ganhos.

        Args:
            instructor_id: ID do usuário instrutor (UUID convertido para string ou UUID)

        Returns:
            InstructorEarningsDTO: Resumo dos ganhos.

        Raises:
            InstructorNotFoundException: Se instrutor não for encontrado.
        """
        # 1. Verificar instrutor
        profile = await self.instructor_repository.get_by_user_id(instructor_id)
        if profile is None:
            raise InstructorNotFoundException(str(instructor_id))

        # 2. Buscar todos os pagamentos (pode ser otimizado com query de agregação no futuro)
        # Por enquanto buscamos lista e somamos na memória (MVP)
        payments = await self.payment_repository.list_by_instructor(
            instructor_id, limit=1000  # Limite alto para pegar histórico recente
        )

        total_earnings = Decimal("0.00")
        pending_earnings = Decimal("0.00")
        completed_lessons = 0

        for payment in payments:
            if payment.status == PaymentStatus.COMPLETED:
                total_earnings += payment.instructor_amount
                completed_lessons += 1
            elif payment.status in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                pending_earnings += payment.instructor_amount

        return InstructorEarningsDTO(
            instructor_id=instructor_id,
            total_earnings=total_earnings,
            pending_earnings=pending_earnings,
            completed_lessons=completed_lessons,
            period_end=datetime.utcnow(),
        )
