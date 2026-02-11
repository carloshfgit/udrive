"""
Request Reschedule Use Case

Caso de uso para aluno solicitar o reagendamento de uma aula.
"""

from dataclasses import dataclass
from datetime import datetime

from src.application.dtos.scheduling_dtos import RequestRescheduleDTO, SchedulingResponseDTO
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingConflictException,
    SchedulingNotFoundException,
    UnavailableSlotException,
    UserNotFoundException,
)
from src.domain.interfaces.availability_repository import IAvailabilityRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class RequestRescheduleUseCase:
    """
    Caso de uso para solicitar reagendamento de aula pelo aluno.

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se usuário é o aluno do agendamento
        3. Validar se estado permite reagendamento (PENDING ou CONFIRMED)
        4. Verificar disponibilidade do instrutor no novo horário
        5. Verificar se não há conflito de horário no novo horário
        6. Atualizar agendamento com a nova data sugerida e status RESCHEDULE_REQUESTED
        7. Retornar SchedulingResponseDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository
    availability_repository: IAvailabilityRepository

    async def execute(self, dto: RequestRescheduleDTO) -> SchedulingResponseDTO:
        """
        Executa a solicitação de reagendamento.

        Args:
            dto: Dados da solicitação.

        Returns:
            SchedulingResponseDTO: Agendamento atualizado.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Verificar se é participante do agendamento (aluno ou instrutor)
        if dto.user_id not in (scheduling.student_id, scheduling.instructor_id):
            raise UserNotFoundException(
                f"Usuário {dto.user_id} não faz parte deste agendamento"
            )

        # 3. Validar estado via entidade (can_request_reschedule já reflete a lógica)
        if not scheduling.can_request_reschedule():
            raise InvalidSchedulingStateException(
                current_state=scheduling.status.value,
                expected_state="pending or confirmed"
            )

        # 4. Verificar disponibilidade configurada
        is_available = await self.availability_repository.is_time_available(
            instructor_id=scheduling.instructor_id,
            target_datetime=dto.new_datetime,
            duration_minutes=scheduling.duration_minutes,
        )
        if not is_available:
            raise UnavailableSlotException(
                "O instrutor não tem disponibilidade configurada para este horário"
            )

        # 5. Verificar conflito de horário
        has_conflict = await self.scheduling_repository.check_conflict(
            instructor_id=scheduling.instructor_id,
            scheduled_datetime=dto.new_datetime,
            duration_minutes=scheduling.duration_minutes,
            exclude_scheduling_id=scheduling.id,  # Excluir o próprio agendamento da checagem
        )
        if has_conflict:
            raise SchedulingConflictException(
                "O instrutor já possui um agendamento neste horário"
            )

        # 6. Solicitar reagendamento
        scheduling.request_reschedule(dto.new_datetime, dto.user_id)
        saved_scheduling = await self.scheduling_repository.update(scheduling)

        # 7. Buscar nomes para resposta enriquecida
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
            rescheduled_datetime=saved_scheduling.rescheduled_datetime,
            rescheduled_by=saved_scheduling.rescheduled_by,
            created_at=saved_scheduling.created_at,
            student_name=student.full_name if student else None,
            instructor_name=instructor.full_name if instructor else None,
        )
