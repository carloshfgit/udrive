"""
Get Student Lessons For Instructor Use Case

Caso de uso para listar todas as aulas que um aluno possui com um instrutor específico.
"""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class GetStudentLessonsForInstructorUseCase:
    """
    Caso de uso para carregar o histórico de aulas entre um instrutor e um aluno.
    Usado na tela de detalhes do aluno dentro do chat.
    """

    scheduling_repository: ISchedulingRepository

    async def execute(self, instructor_id: UUID, student_id: UUID) -> list[SchedulingResponseDTO]:
        """
        Lista todas as aulas entre o instrutor e o aluno.
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
