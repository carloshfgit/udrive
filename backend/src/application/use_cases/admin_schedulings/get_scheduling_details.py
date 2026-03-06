"""
Get Scheduling Details Use Case

Obtém detalhes completos de um agendamento para o admin panel.
"""

from uuid import UUID

from src.application.dtos.admin_scheduling_dtos import SchedulingAdminResponseDTO
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


class GetSchedulingDetailsUseCase:
    """Obtém detalhes de um agendamento para o painel administrativo."""

    def __init__(self, scheduling_repository: ISchedulingRepository) -> None:
        self._scheduling_repo = scheduling_repository

    async def execute(self, scheduling_id: UUID) -> SchedulingAdminResponseDTO | None:
        """Busca detalhes completos de um agendamento."""
        scheduling = await self._scheduling_repo.get_by_id(scheduling_id)
        if scheduling is None:
            return None

        return SchedulingAdminResponseDTO(
            id=scheduling.id,
            student_id=scheduling.student_id,
            instructor_id=scheduling.instructor_id,
            scheduled_datetime=scheduling.scheduled_datetime,
            status=scheduling.status.value if hasattr(scheduling.status, "value") else scheduling.status,
            price=float(scheduling.price),
            duration_minutes=scheduling.duration_minutes,
            student_name=scheduling.student_name,
            instructor_name=scheduling.instructor_name,
            payment_status=scheduling.payment_status or "none",
            lesson_category=scheduling.lesson_category.value if scheduling.lesson_category and hasattr(scheduling.lesson_category, "value") else str(scheduling.lesson_category) if scheduling.lesson_category else None,
            vehicle_ownership=scheduling.vehicle_ownership.value if scheduling.vehicle_ownership and hasattr(scheduling.vehicle_ownership, "value") else str(scheduling.vehicle_ownership) if scheduling.vehicle_ownership else None,
            applied_base_price=float(scheduling.applied_base_price) if scheduling.applied_base_price else None,
            applied_final_price=float(scheduling.applied_final_price) if scheduling.applied_final_price else None,
            cancellation_reason=scheduling.cancellation_reason,
            cancelled_by=scheduling.cancelled_by,
            cancelled_at=scheduling.cancelled_at,
            completed_at=scheduling.completed_at,
            started_at=scheduling.started_at,
            student_confirmed_at=scheduling.student_confirmed_at,
            created_at=scheduling.created_at,
            updated_at=scheduling.updated_at,
        )
