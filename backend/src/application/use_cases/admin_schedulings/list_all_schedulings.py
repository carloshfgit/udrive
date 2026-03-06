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
                price=float(s.price),
                duration_minutes=s.duration_minutes,
                student_name=s.student_name,
                instructor_name=s.instructor_name,
                payment_status=s.payment_status or "none",
                lesson_category=s.lesson_category.value if s.lesson_category and hasattr(s.lesson_category, "value") else str(s.lesson_category) if s.lesson_category else None,
                vehicle_ownership=s.vehicle_ownership.value if s.vehicle_ownership and hasattr(s.vehicle_ownership, "value") else str(s.vehicle_ownership) if s.vehicle_ownership else None,
                applied_base_price=float(s.applied_base_price) if s.applied_base_price else None,
                applied_final_price=float(s.applied_final_price) if s.applied_final_price else None,
                cancellation_reason=s.cancellation_reason,
                cancelled_by=s.cancelled_by,
                cancelled_at=s.cancelled_at,
                completed_at=s.completed_at,
                started_at=s.started_at,
                student_confirmed_at=s.student_confirmed_at,
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
