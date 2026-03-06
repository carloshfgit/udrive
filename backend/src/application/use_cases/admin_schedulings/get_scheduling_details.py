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
            price=scheduling.price,
            student_name=scheduling.student_name,
            instructor_name=scheduling.instructor_name,
            payment_status=scheduling.payment_status or "none",
            created_at=scheduling.created_at,
            updated_at=scheduling.updated_at,
        )
