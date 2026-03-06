"""
List All Schedulings Use Case

Lista todos os agendamentos do sistema com filtros e paginação para o admin panel.
"""

from src.application.dtos.admin_scheduling_dtos import (
    ListAllSchedulingsDTO,
    SchedulingAdminResponseDTO,
    SchedulingListResponseDTO,
)
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


class ListAllSchedulingsUseCase:
    """Lista todos os agendamentos do sistema para o painel administrativo."""

    def __init__(self, scheduling_repository: ISchedulingRepository) -> None:
        self._scheduling_repo = scheduling_repository

    async def execute(self, dto: ListAllSchedulingsDTO) -> SchedulingListResponseDTO:
        """Executa a listagem de agendamentos."""
        schedulings = await self._scheduling_repo.list_all(
            status=dto.status,
            student_id=dto.student_id,
            instructor_id=dto.instructor_id,
            date_from=dto.date_from,
            date_to=dto.date_to,
            limit=dto.limit,
            offset=dto.offset,
        )

        total_count = await self._scheduling_repo.count_all(
            status=dto.status,
            student_id=dto.student_id,
            instructor_id=dto.instructor_id,
            date_from=dto.date_from,
            date_to=dto.date_to,
        )

        scheduling_dtos = [
            SchedulingAdminResponseDTO(
                id=s.id,
                student_id=s.student_id,
                instructor_id=s.instructor_id,
                scheduled_datetime=s.scheduled_datetime,
                status=s.status.value if hasattr(s.status, "value") else s.status,
                price=s.price,
                student_name=s.student_name,
                instructor_name=s.instructor_name,
                payment_status=s.payment_status or "none",
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in schedulings
        ]

        return SchedulingListResponseDTO(
            schedulings=scheduling_dtos,
            total_count=total_count,
            limit=dto.limit,
            offset=dto.offset,
            has_more=(dto.offset + dto.limit) < total_count,
        )
