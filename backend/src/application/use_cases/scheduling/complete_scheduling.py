"""
Complete Scheduling Use Case

Caso de uso para marcar um agendamento como concluído.
"""

from dataclasses import dataclass
from datetime import datetime

from src.application.dtos.scheduling_dtos import CompleteSchedulingDTO, SchedulingResponseDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class CompleteSchedulingUseCase:
    """
    Caso de uso para marcar um agendamento como concluído.

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se está CONFIRMED
        3. Verificar se usuário é o instrutor do agendamento
        4. Validar que a data/hora agendada já passou
        5. Atualizar status para COMPLETED
        6. Retornar SchedulingResponseDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    async def execute(self, dto: CompleteSchedulingDTO) -> SchedulingResponseDTO:
        """
        Executa a conclusão do agendamento.

        Args:
            dto: Dados da conclusão.

        Returns:
            SchedulingResponseDTO: Agendamento concluído.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            InvalidSchedulingStateException: Se não estiver CONFIRMED ou aula não acabou.
            UserNotFoundException: Se não for o instrutor do agendamento.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Validar estado
        if scheduling.status != SchedulingStatus.CONFIRMED:
            raise InvalidSchedulingStateException(
                current_state=scheduling.status.value,
                expected_state="confirmed"
            )

        # 3. Verificar se é o instrutor
        if dto.instructor_id != scheduling.instructor_id:
            raise UserNotFoundException(
                f"Usuário {dto.instructor_id} não é o instrutor deste agendamento"
            )

        # 4. Validar que a aula já terminou
        now = datetime.utcnow()
        if now < scheduling.lesson_end_datetime:
            raise InvalidSchedulingStateException(
                current_state="aula ainda não terminou",
                expected_state="aula concluída"
            )

        # 5. Completar
        scheduling.complete()
        saved_scheduling = await self.scheduling_repository.update(scheduling)

        # 6. Buscar nomes para resposta enriquecida
        student = await self.user_repository.get_by_id(saved_scheduling.student_id)
        instructor = await self.user_repository.get_by_id(saved_scheduling.instructor_id)

        return SchedulingResponseDTO(
            id=saved_scheduling.id,
            student_id=saved_scheduling.student_id,
            instructor_id=saved_scheduling.instructor_id,
            scheduled_datetime=saved_scheduling.scheduled_datetime,
            duration_minutes=saved_scheduling.duration_minutes,
            price=saved_scheduling.price,
            status=saved_scheduling.status.value,
            completed_at=saved_scheduling.completed_at,
            created_at=saved_scheduling.created_at,
            student_name=student.full_name if student else None,
            instructor_name=instructor.full_name if instructor else None,
        )
