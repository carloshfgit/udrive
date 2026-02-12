"""
Get Next Student Scheduling Use Case
"""

from uuid import UUID
from src.domain.entities.scheduling import Scheduling
from src.domain.interfaces.scheduling_repository import ISchedulingRepository

class GetNextStudentSchedulingUseCase:
    """
    Use case to fetch the next upcoming scheduling for a student.
    """

    def __init__(self, scheduling_repository: ISchedulingRepository) -> None:
        self._scheduling_repository = scheduling_repository

    async def execute(self, student_id: UUID) -> Scheduling | None:
        """
        Executes the use case to find the next scheduling.
        """
        return await self._scheduling_repository.get_next_student_scheduling(student_id)
