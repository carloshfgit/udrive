"""
Cancel Scheduling Use Case

Caso de uso para cancelar um agendamento com regras de reembolso.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.application.dtos.scheduling_dtos import CancelSchedulingDTO, CancellationResultDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingAlreadyCancelledException,
    SchedulingAlreadyCompletedException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class CancelSchedulingUseCase:
    """
    Caso de uso para cancelar um agendamento.

    Regras de reembolso:
        - > 24h antes da aula: 100% reembolso
        - < 24h antes da aula: 50% reembolso (multa de 50%)

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se pode ser cancelado
        3. Verificar se usuário tem permissão
        4. Calcular percentual de reembolso
        5. Atualizar status para CANCELLED
        6. Retornar CancellationResultDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    async def execute(self, dto: CancelSchedulingDTO) -> CancellationResultDTO:
        """
        Executa o cancelamento do agendamento.

        Args:
            dto: Dados do cancelamento.

        Returns:
            CancellationResultDTO: Resultado com informações de reembolso.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            SchedulingAlreadyCancelledException: Se já foi cancelado.
            SchedulingAlreadyCompletedException: Se já foi concluído.
            UserNotFoundException: Se usuário não tiver permissão.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Validar estado atual
        if scheduling.status == SchedulingStatus.CANCELLED:
            raise SchedulingAlreadyCancelledException()

        if scheduling.status == SchedulingStatus.COMPLETED:
            raise SchedulingAlreadyCompletedException()

        if not scheduling.can_cancel():
            raise InvalidSchedulingStateException(
                current_state=scheduling.status.value,
                expected_state="pending ou confirmed"
            )

        # 3. Verificar permissão (deve ser o aluno ou instrutor do agendamento)
        if dto.cancelled_by not in (scheduling.student_id, scheduling.instructor_id):
            # Verificar se o usuário existe
            user = await self.user_repository.get_by_id(dto.cancelled_by)
            if user is None:
                raise UserNotFoundException(str(dto.cancelled_by))
            raise UserNotFoundException(
                f"Usuário {dto.cancelled_by} não tem permissão para cancelar este agendamento"
            )

        # 4. Calcular reembolso
        refund_percentage = scheduling.calculate_refund_percentage()
        refund_amount = (scheduling.price * Decimal(refund_percentage)) / Decimal(100)

        # 5. Cancelar
        scheduling.cancel(
            cancelled_by=dto.cancelled_by,
            reason=dto.reason,
        )

        await self.scheduling_repository.update(scheduling)

        # 6. Retornar resultado
        return CancellationResultDTO(
            scheduling_id=scheduling.id,
            status=scheduling.status.value,
            refund_percentage=refund_percentage,
            refund_amount=refund_amount,
            cancelled_at=scheduling.cancelled_at or datetime.utcnow(),
        )
