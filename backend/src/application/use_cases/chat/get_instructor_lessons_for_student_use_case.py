"""
Get Instructor Lessons For Student Use Case

Caso de uso para listar todas as aulas que um aluno possui com um instrutor específico.
"""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class GetInstructorLessonsForStudentUseCase:
    """
    Caso de uso para carregar o histórico de aulas entre um aluno e um instrutor.
    Usado na tela de chat quando o aluno clica em "Ver Aulas".
    """

    scheduling_repository: ISchedulingRepository

    async def execute(self, student_id: UUID, instructor_id: UUID) -> list[SchedulingResponseDTO]:
        """
        Lista todas as aulas entre o aluno e o instrutor.
        """
        schedulings = await self.scheduling_repository.list_by_student_and_instructor(
            student_id=student_id,
            instructor_id=instructor_id,
            limit=100
        )

        return [
            SchedulingResponseDTO(
                id=s.id,
                student_id=s.student_id,
                instructor_id=s.instructor_id,
                scheduled_datetime=s.scheduled_datetime,
                duration_minutes=s.duration_minutes,
                price=s.price,
                status=s.status.value,
                cancellation_reason=s.cancellation_reason,
                cancelled_by=s.cancelled_by,
                cancelled_at=s.cancelled_at,
                completed_at=s.completed_at,
                created_at=s.created_at,
                student_name=s.student_name,
                instructor_name=s.instructor_name,
            )
            for s in schedulings
        ]
