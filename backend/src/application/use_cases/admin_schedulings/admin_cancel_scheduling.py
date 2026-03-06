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
            price=updated.price,
            student_name=updated.student_name,
            instructor_name=updated.instructor_name,
            payment_status=updated.payment_status or "none",
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
