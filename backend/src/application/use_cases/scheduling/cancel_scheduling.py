"""
Cancel Scheduling Use Case

Caso de uso para cancelar um agendamento com regras de reembolso.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from src.application.dtos.scheduling_dtos import CancelSchedulingDTO, CancellationResultDTO
from src.application.dtos.payment_dtos import ProcessRefundDTO
from src.application.use_cases.payment.process_refund import ProcessRefundUseCase
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    InvalidSchedulingStateException,
    SchedulingAlreadyCancelledException,
    SchedulingAlreadyCompletedException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class CancelSchedulingUseCase:
    """
    Caso de uso para cancelar um agendamento.

    Regras de reembolso (PAYMENT_FLOW.md):
        - >= 48h antes da aula: 100% reembolso
        - Entre 24h e 48h: 50% reembolso
        - < 24h antes da aula: 0% reembolso
        - Emergência: marcado para revisão manual

    Fluxo:
        1. Buscar agendamento por ID
        2. Validar se pode ser cancelado
        3. Verificar se usuário tem permissão
        4. Calcular percentual de reembolso
        5. Atualizar status para CANCELLED
        6. Se existe pagamento, processar refund via Stripe
        7. Retornar CancellationResultDTO
    """

    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository
    payment_repository: IPaymentRepository
    process_refund_use_case: ProcessRefundUseCase

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

        # 6. Processar reembolso via Stripe (se há pagamento associado)
        emergency_refund_requested = False

        payment = await self.payment_repository.get_by_scheduling_id(dto.scheduling_id)
        if payment is not None and refund_percentage > 0:
            if dto.is_emergency:
                # Emergência: marcar para revisão manual, não refundar automaticamente
                emergency_refund_requested = True
            else:
                # Refund automático via Stripe
                refund_dto = ProcessRefundDTO(
                    payment_id=payment.id,
                    reason=dto.reason or "Cancelamento de aula",
                    refund_percentage=refund_percentage,
                )
                await self.process_refund_use_case.execute(refund_dto)

        # 7. Retornar resultado
        return CancellationResultDTO(
            scheduling_id=scheduling.id,
            status=scheduling.status.value,
            refund_percentage=refund_percentage,
            refund_amount=refund_amount,
            cancelled_at=scheduling.cancelled_at or datetime.now(timezone.utc),
            emergency_refund_requested=emergency_refund_requested,
        )

