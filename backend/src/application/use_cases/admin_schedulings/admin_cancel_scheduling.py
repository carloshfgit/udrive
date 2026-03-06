"""
Admin Cancel Scheduling Use Case

Cancela um agendamento por ação administrativa.
Diferente do cancelamento comum, o admin pode cancelar a qualquer momento sem restrições.
"""

from datetime import datetime

import structlog

from src.application.dtos.admin_scheduling_dtos import (
    AdminCancelSchedulingDTO,
    SchedulingAdminResponseDTO,
)
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.scheduling_repository import ISchedulingRepository

logger = structlog.get_logger()


class SchedulingNotFoundException(Exception):
    """Exceção para agendamento não encontrado."""

    pass


class AdminCancelSchedulingUseCase:
    """Cancela um agendamento como administrador."""

    def __init__(self, scheduling_repository: ISchedulingRepository) -> None:
        self._scheduling_repo = scheduling_repository

    async def execute(self, dto: AdminCancelSchedulingDTO) -> SchedulingAdminResponseDTO:
        """Executa o cancelamento administrativo."""
        scheduling = await self._scheduling_repo.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(
                f"Agendamento não encontrado: {dto.scheduling_id}"
            )

        # Atualizar status para cancelado
        scheduling.status = SchedulingStatus.CANCELLED
        scheduling.cancelled_by = dto.admin_id
        scheduling.cancelled_at = datetime.utcnow()
        scheduling.cancellation_reason = f"[ADMIN] {dto.reason}"
        scheduling.updated_at = datetime.utcnow()

        updated = await self._scheduling_repo.update(scheduling)

        logger.info(
            "admin_cancel_scheduling",
            scheduling_id=str(dto.scheduling_id),
            admin_id=str(dto.admin_id),
            reason=dto.reason,
        )

        return SchedulingAdminResponseDTO(
            id=updated.id,
            student_id=updated.student_id,
            instructor_id=updated.instructor_id,
            scheduled_datetime=updated.scheduled_datetime,
            status=updated.status.value if hasattr(updated.status, "value") else updated.status,
            price=float(updated.price),
            duration_minutes=updated.duration_minutes,
            student_name=updated.student_name,
            instructor_name=updated.instructor_name,
            payment_status=updated.payment_status or "none",
            lesson_category=updated.lesson_category.value if updated.lesson_category and hasattr(updated.lesson_category, "value") else str(updated.lesson_category) if updated.lesson_category else None,
            vehicle_ownership=updated.vehicle_ownership.value if updated.vehicle_ownership and hasattr(updated.vehicle_ownership, "value") else str(updated.vehicle_ownership) if updated.vehicle_ownership else None,
            applied_base_price=float(updated.applied_base_price) if updated.applied_base_price else None,
            applied_final_price=float(updated.applied_final_price) if updated.applied_final_price else None,
            cancellation_reason=updated.cancellation_reason,
            cancelled_by=updated.cancelled_by,
            cancelled_at=updated.cancelled_at,
            completed_at=updated.completed_at,
            started_at=updated.started_at,
            student_confirmed_at=updated.student_confirmed_at,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
