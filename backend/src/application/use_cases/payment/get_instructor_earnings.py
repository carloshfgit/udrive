"""
Get Instructor Earnings Use Case

Caso de uso para obter os ganhos financeiros do instrutor.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from src.application.dtos.payment_dtos import InstructorEarningsDTO
from src.domain.entities.payment_status import PaymentStatus
from src.domain.entities.scheduling_status import SchedulingStatus
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
        3. Calcular total de ganhos (todos os pagamentos completados)
        4. Calcular ganhos do mês corrente (pagamentos completados no mês atual)
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
        # Filtrar estritamente apenas quando a própria aula também foi completada
        payments = await self.payment_repository.list_by_instructor(
            instructor_id,
            status=PaymentStatus.COMPLETED,
            scheduling_status=SchedulingStatus.COMPLETED,
            limit=1000,  # Limite alto para pegar histórico recente
        )

        now = datetime.now(tz=timezone.utc)
        current_year = now.year
        current_month = now.month

        total_earnings = Decimal("0.00")
        monthly_earnings = Decimal("0.00")
        completed_lessons = len(payments)

        for payment in payments:
            total_earnings += payment.instructor_amount

            # Verificar se o pagamento é do mês corrente
            created = payment.created_at
            if created is not None:
                # Normalizar para UTC caso seja offset-naive
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created.year == current_year and created.month == current_month:
                    monthly_earnings += payment.instructor_amount

        base_lesson_price = None
        if profile.price_cat_b_instructor_vehicle is not None:
            base_lesson_price = profile.price_cat_b_instructor_vehicle
        elif profile.price_cat_b_student_vehicle is not None:
            base_lesson_price = profile.price_cat_b_student_vehicle
        elif profile.price_cat_a_instructor_vehicle is not None:
            base_lesson_price = profile.price_cat_a_instructor_vehicle
        elif profile.price_cat_a_student_vehicle is not None:
            base_lesson_price = profile.price_cat_a_student_vehicle

        return InstructorEarningsDTO(
            instructor_id=instructor_id,
            total_earnings=total_earnings,
            monthly_earnings=monthly_earnings,
            completed_lessons=completed_lessons,
            base_lesson_price=base_lesson_price,
            period_start=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            period_end=now,
        )
