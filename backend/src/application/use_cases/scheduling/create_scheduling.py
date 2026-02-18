"""
Create Scheduling Use Case

Caso de uso para criar um novo agendamento de aula.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.application.dtos.scheduling_dtos import CreateSchedulingDTO, SchedulingResponseDTO
from src.domain.entities.scheduling import Scheduling
from src.domain.entities.user_type import UserType
from src.domain.exceptions import (
    InstructorNotFoundException,
    SchedulingConflictException,
    StudentNotFoundException,
    UnavailableSlotException,
    UserNotFoundException,
)
from src.domain.interfaces.availability_repository import IAvailabilityRepository
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.services.pricing_service import PricingService


@dataclass
class CreateSchedulingUseCase:
    """
    Caso de uso para criar um novo agendamento de aula.

    Fluxo:
        1. Validar se aluno existe e está ativo
        2. Validar se instrutor existe, está ativo e é instrutor
        3. Verificar disponibilidade do instrutor no horário
        4. Verificar se não há conflito de horário
        5. Calcular preço (hourly_rate * duração)
        6. Criar agendamento com status PENDING
        7. Retornar SchedulingResponseDTO
    """

    user_repository: IUserRepository
    instructor_repository: IInstructorRepository
    scheduling_repository: ISchedulingRepository
    availability_repository: IAvailabilityRepository

    async def execute(self, dto: CreateSchedulingDTO) -> SchedulingResponseDTO:
        """
        Executa a criação do agendamento.

        Args:
            dto: Dados do agendamento a criar.

        Returns:
            SchedulingResponseDTO: Agendamento criado.

        Raises:
            StudentNotFoundException: Se aluno não existir ou não for aluno.
            InstructorNotFoundException: Se instrutor não existir ou não for instrutor.
            UnavailableSlotException: Se o horário não estiver na disponibilidade.
            SchedulingConflictException: Se houver conflito de horário.
        """
        # 1. Validar aluno
        student = await self.user_repository.get_by_id(dto.student_id)
        if student is None:
            raise StudentNotFoundException(str(dto.student_id))
        if student.user_type != UserType.STUDENT:
            raise StudentNotFoundException(f"Usuário {dto.student_id} não é um aluno")
        if not student.is_active:
            raise StudentNotFoundException("Aluno está inativo")

        # 2. Validar instrutor
        instructor = await self.user_repository.get_by_id(dto.instructor_id)
        if instructor is None:
            raise InstructorNotFoundException(str(dto.instructor_id))
        if instructor.user_type != UserType.INSTRUCTOR:
            raise InstructorNotFoundException(
                f"Usuário {dto.instructor_id} não é um instrutor"
            )
        if not instructor.is_active:
            raise InstructorNotFoundException("Instrutor está inativo")

        # Buscar perfil do instrutor para obter hourly_rate
        instructor_profile = await self.instructor_repository.get_by_user_id(
            dto.instructor_id
        )
        if instructor_profile is None:
            raise InstructorNotFoundException(
                f"Perfil do instrutor {dto.instructor_id} não encontrado"
            )
        if not instructor_profile.is_available:
            raise UnavailableSlotException("Instrutor não está aceitando novos alunos")

        # 3. Verificar disponibilidade configurada
        is_available = await self.availability_repository.is_time_available(
            instructor_id=dto.instructor_id,
            target_datetime=dto.scheduled_datetime,
            duration_minutes=dto.duration_minutes,
        )
        if not is_available:
            raise UnavailableSlotException(
                "O instrutor não tem disponibilidade configurada para este horário"
            )

        # 4. Verificar conflito de horário
        has_conflict = await self.scheduling_repository.check_conflict(
            instructor_id=dto.instructor_id,
            scheduled_datetime=dto.scheduled_datetime,
            duration_minutes=dto.duration_minutes,
        )
        if has_conflict:
            raise SchedulingConflictException(
                "O instrutor já possui um agendamento neste horário"
            )

        # 5. Calcular preço
        hours = Decimal(dto.duration_minutes) / Decimal(60)
        base_price = instructor_profile.hourly_rate * hours
        price = PricingService.calculate_final_price(base_price)

        # 6. Criar agendamento
        scheduling = Scheduling(
            student_id=dto.student_id,
            instructor_id=dto.instructor_id,
            scheduled_datetime=dto.scheduled_datetime,
            duration_minutes=dto.duration_minutes,
            price=price,
        )

        saved_scheduling = await self.scheduling_repository.create(scheduling)

        # 7. Retornar resposta
        return SchedulingResponseDTO(
            id=saved_scheduling.id,
            student_id=saved_scheduling.student_id,
            instructor_id=saved_scheduling.instructor_id,
            scheduled_datetime=saved_scheduling.scheduled_datetime,
            duration_minutes=saved_scheduling.duration_minutes,
            price=saved_scheduling.price,
            status=saved_scheduling.status.value,
            created_at=saved_scheduling.created_at,
            student_name=student.full_name,
            instructor_name=instructor.full_name,
        )
