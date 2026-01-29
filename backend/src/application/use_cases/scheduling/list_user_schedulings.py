"""
List User Schedulings Use Case

Caso de uso para listar agendamentos de um usuário (histórico).
"""

from dataclasses import dataclass

from src.application.dtos.scheduling_dtos import (
    ListSchedulingsDTO,
    SchedulingListResponseDTO,
    SchedulingResponseDTO,
)
from src.domain.entities.user_type import UserType
from src.domain.exceptions import UserNotFoundException
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class ListUserSchedulingsUseCase:
    """
    Caso de uso para listar agendamentos de um usuário.

    Identifica o tipo de usuário (aluno ou instrutor) e
    retorna os agendamentos correspondentes com paginação.
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    async def execute(self, dto: ListSchedulingsDTO) -> SchedulingListResponseDTO:
        """
        Executa a listagem de agendamentos.

        Args:
            dto: Filtros de listagem.

        Returns:
            SchedulingListResponseDTO: Lista paginada de agendamentos.

        Raises:
            UserNotFoundException: Se usuário não existir.
        """
        # Buscar usuário para identificar tipo
        user = await self.user_repository.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundException(str(dto.user_id))

        # Buscar agendamentos baseado no tipo de usuário
        if user.user_type == UserType.STUDENT:
            schedulings = await self.scheduling_repository.list_by_student(
                student_id=dto.user_id,
                status=dto.status,
                limit=dto.limit,
                offset=dto.offset,
            )
            total_count = await self.scheduling_repository.count_by_student(
                student_id=dto.user_id,
                status=dto.status,
            )
        elif user.user_type == UserType.INSTRUCTOR:
            schedulings = await self.scheduling_repository.list_by_instructor(
                instructor_id=dto.user_id,
                status=dto.status,
                limit=dto.limit,
                offset=dto.offset,
            )
            total_count = await self.scheduling_repository.count_by_instructor(
                instructor_id=dto.user_id,
                status=dto.status,
            )
        else:
            # Admin pode ver todos (implementação futura)
            raise UserNotFoundException(
                f"Tipo de usuário {user.user_type} não suportado para listagem"
            )

        # Converter para DTOs de resposta
        scheduling_dtos = []
        for scheduling in schedulings:
            # Buscar nomes para enriquecer resposta
            student = await self.user_repository.get_by_id(scheduling.student_id)
            instructor = await self.user_repository.get_by_id(scheduling.instructor_id)

            scheduling_dtos.append(
                SchedulingResponseDTO(
                    id=scheduling.id,
                    student_id=scheduling.student_id,
                    instructor_id=scheduling.instructor_id,
                    scheduled_datetime=scheduling.scheduled_datetime,
                    duration_minutes=scheduling.duration_minutes,
                    price=scheduling.price,
                    status=scheduling.status.value,
                    cancellation_reason=scheduling.cancellation_reason,
                    cancelled_by=scheduling.cancelled_by,
                    cancelled_at=scheduling.cancelled_at,
                    completed_at=scheduling.completed_at,
                    created_at=scheduling.created_at,
                    student_name=student.full_name if student else None,
                    instructor_name=instructor.full_name if instructor else None,
                )
            )

        has_more = dto.offset + len(schedulings) < total_count

        return SchedulingListResponseDTO(
            schedulings=scheduling_dtos,
            total_count=total_count,
            limit=dto.limit,
            offset=dto.offset,
            has_more=has_more,
        )
