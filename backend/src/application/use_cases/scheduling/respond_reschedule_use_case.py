"""
Respond Reschedule Use Case

Caso de uso para instrutor responder a uma solicitação de reagendamento.
"""

from dataclasses import dataclass

from src.application.dtos.scheduling_dtos import RespondRescheduleDTO, SchedulingResponseDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository
from src.domain.interfaces.availability_repository import IAvailabilityRepository


@dataclass
class RespondRescheduleUseCase:
    """
    Caso de uso para responder a uma solicitação de reagendamento de aula pelo instrutor.

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se usuário é o instrutor do agendamento
        3. Validar se estado é RESCHEDULE_REQUESTED
        4. Se aceito:
            - Verificar disponibilidade do instrutor no novo horário
            - Verificar se não há conflito de horário no novo horário
            - Chamar accept_reschedule() na entidade
        5. Se recusado:
            - Chamar refuse_reschedule() na entidade
        6. Salvar alteração no repositório
        7. Retornar SchedulingResponseDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository
    availability_repository: IAvailabilityRepository

    async def execute(self, dto: RespondRescheduleDTO) -> SchedulingResponseDTO:
        """
        Executa a resposta ao reagendamento.

        Args:
            dto: Dados da resposta.

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

        # 2b. Verificar se não é quem solicitou o reagendamento (exceto se for para cancelar/recusar seu próprio pedido)
        if dto.user_id == scheduling.rescheduled_by and dto.accepted:
            raise ValueError(
                f"Usuário {dto.user_id} não pode aceitar seu próprio pedido de reagendamento"
            )

        # 3. Validar estado
        if scheduling.status != SchedulingStatus.RESCHEDULE_REQUESTED:
            raise InvalidSchedulingStateException(
                current_state=scheduling.status.value,
                expected_state="reschedule_requested"
            )

        # 4 & 5. Processar decisão
        if dto.accepted:
            # Check for generic exceptions if new datetime is missing
            if not scheduling.rescheduled_datetime:
                raise ValueError("Data de reagendamento não encontrada")

            # Validate availability at the new time
            is_available = await self.availability_repository.is_time_available(
                instructor_id=scheduling.instructor_id,
                target_datetime=scheduling.rescheduled_datetime,
                duration_minutes=scheduling.duration_minutes,
            )
            if not is_available:
                from src.domain.exceptions import UnavailableSlotException
                raise UnavailableSlotException(
                    "O instrutor não tem mais disponibilidade configurada para este horário"
                )

            # Validate conflicts at the new time
            has_conflict = await self.scheduling_repository.check_conflict(
                instructor_id=scheduling.instructor_id,
                scheduled_datetime=scheduling.rescheduled_datetime,
                duration_minutes=scheduling.duration_minutes,
                exclude_scheduling_id=scheduling.id,
            )
            if has_conflict:
                from src.domain.exceptions import SchedulingConflictException
                raise SchedulingConflictException(
                    "Ops! Outro aluno já agendou nesse horário, tentem combinar um horário diferente."
                )

            scheduling.accept_reschedule()
        else:
            scheduling.refuse_reschedule()

        # 6. Salvar
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
