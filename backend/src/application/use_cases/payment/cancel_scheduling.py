"""
Cancel Scheduling Use Case

Caso de uso que orquestra o fluxo completo de cancelamento:
cancela o agendamento e processa o reembolso conforme as regras de negócio.
"""

from dataclasses import dataclass

from src.application.dtos.payment_dtos import (
    CancelSchedulingDTO,
    CancelSchedulingResultDTO,
    ProcessRefundDTO,
)
from src.application.use_cases.payment.process_refund import ProcessRefundUseCase
from src.domain.exceptions import (
    SchedulingNotFoundException,
    CancellationException,
)
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class CancelSchedulingUseCase:
    """
    Caso de uso para cancelar agendamento com reembolso automático.

    Fluxo:
        1. Buscar Scheduling pelo scheduling_id
        2. Validar se pode cancelar (can_cancel)
        3. Calcular refund_percentage via regras de domínio
        4. Cancelar scheduling (muda status para CANCELLED)
        5. Se refund_percentage > 0 e houver Payment → processar reembolso via MP
        6. Retornar resultado
    """

    scheduling_repository: ISchedulingRepository
    payment_repository: IPaymentRepository
    process_refund_use_case: ProcessRefundUseCase

    async def execute(self, dto: CancelSchedulingDTO) -> CancelSchedulingResultDTO:
        """
        Executa o cancelamento do agendamento.

        Args:
            dto: Dados do cancelamento.

        Returns:
            CancelSchedulingResultDTO com resultado.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            CancellationException: Se não puder ser cancelado.
        """
        # 1. Buscar Scheduling
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Validar se pode cancelar
        if not scheduling.can_cancel():
            raise CancellationException(
                f"Agendamento não pode ser cancelado. Status: {scheduling.status}"
            )

        # 3. Calcular percentual de reembolso
        refund_percentage = scheduling.calculate_refund_percentage()

        # 4. Cancelar scheduling
        scheduling.cancel(cancelled_by=dto.cancelled_by, reason=dto.reason)
        await self.scheduling_repository.update(scheduling)

        # 5. Processar reembolso (se > 0%)
        refund_amount = None
        refund_status = None

        if refund_percentage > 0:
            # Buscar Payment associado ao scheduling
            payment = await self.payment_repository.get_by_scheduling_id(
                dto.scheduling_id
            )

            if payment and payment.can_refund():
                refund_dto = ProcessRefundDTO(
                    payment_id=payment.id,
                    refund_percentage=refund_percentage,
                    reason=dto.reason,
                )
                refund_result = await self.process_refund_use_case.execute(refund_dto)
                refund_amount = refund_result.refund_amount
                refund_status = refund_result.status

        # 6. Retornar resultado
        return CancelSchedulingResultDTO(
            scheduling_id=dto.scheduling_id,
            status="cancelled",
            refund_percentage=refund_percentage,
            refund_amount=refund_amount,
            refund_status=refund_status,
        )
