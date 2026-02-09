"""
Instructor Students Router

Endpoints para o instrutor gerenciar e visualizar detalhes de seus alunos.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
from src.application.use_cases.chat.get_student_lessons_for_instructor_use_case import (
    GetStudentLessonsForInstructorUseCase,
)
from src.interface.api.dependencies import (
    CurrentInstructor,
    get_get_student_lessons_for_instructor_use_case,
)

router = APIRouter(prefix="/students", tags=["Instructor Students"])


@router.get("/{student_id}/lessons", response_model=list[SchedulingResponseDTO])
async def list_student_lessons(
    student_id: UUID,
    current_instructor: CurrentInstructor,
    use_case: Annotated[
        GetStudentLessonsForInstructorUseCase,
        Depends(get_get_student_lessons_for_instructor_use_case),
    ],
) -> list[SchedulingResponseDTO]:
    """
    Retorna o histórico completo de aulas entre o instrutor logado e um aluno específico.
    """
    return await use_case.execute(current_instructor.id, student_id)
