"""
Confirm Scheduling Use Case

Caso de uso para confirmação de agendamento pelo instrutor.
"""

from dataclasses import dataclass

from src.application.dtos.scheduling_dtos import ConfirmSchedulingDTO, SchedulingResponseDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class ConfirmSchedulingUseCase:
    """
    Caso de uso para confirmação de agendamento pelo instrutor.

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se está PENDING
        3. Verificar se usuário é o instrutor do agendamento
        4. Atualizar status para CONFIRMED
        5. Retornar SchedulingResponseDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    async def execute(self, dto: ConfirmSchedulingDTO) -> SchedulingResponseDTO:
        """
        Executa a confirmação do agendamento.

        Args:
            dto: Dados da confirmação.

        Returns:
            SchedulingResponseDTO: Agendamento confirmado.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            InvalidSchedulingStateException: Se não estiver PENDING.
            UserNotFoundException: Se não for o instrutor do agendamento.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Validar estado
        if scheduling.status != SchedulingStatus.PENDING:
            raise InvalidSchedulingStateException(
                current_state=scheduling.status.value,
                expected_state="pending"
            )

        # 3. Verificar se é o instrutor
        if dto.instructor_id != scheduling.instructor_id:
            raise UserNotFoundException(
                f"Usuário {dto.instructor_id} não é o instrutor deste agendamento"
            )

        # 4. Confirmar
        scheduling.confirm()
        saved_scheduling = await self.scheduling_repository.update(scheduling)

        # 5. Buscar nomes para resposta enriquecida
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
            created_at=saved_scheduling.created_at,
            student_name=student.full_name if student else None,
            instructor_name=instructor.full_name if instructor else None,
        )
