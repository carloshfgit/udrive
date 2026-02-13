"""
Create Dispute Use Case

Caso de uso para permitir que um aluno reporte um problema com uma aula,
colocando o agendamento e o pagamento em estado de disputa.
"""

from dataclasses import dataclass
from src.application.dtos.payment_dtos import CreateDisputeDTO
from src.domain.exceptions import (
    DomainException,
    PaymentNotFoundException,
    SchedulingNotFoundException,
)
from src.domain.interfaces.payment_repository import IPaymentRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class CreateDisputeUseCase:
    """
    Caso de uso para criar uma disputa de aula.

    Fluxo:
        1. Buscar agendamento e validar se pertence ao aluno
        2. Buscar pagamento associado
        3. Validar se a aula pode ser disputada (está confirmada ou concluída)
        4. Alterar status do agendamento para DISPUTED
        5. Alterar status do pagamento para DISPUTED
        6. Salvar ambos
    """

    scheduling_repository: ISchedulingRepository
    payment_repository: IPaymentRepository

    async def execute(self, dto: CreateDisputeDTO) -> None:
        """
        Executa a criação da disputa.

        Args:
            dto: Dados da disputa.

        Raises:
            SchedulingNotFoundException: Se o agendamento não existe.
            PaymentNotFoundException: Se o pagamento não existe.
            DomainException: Se a aula não pertence ao aluno ou não pode ser disputada.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # Validar pertencimento
        if scheduling.student_id != dto.student_id:
            raise DomainException("Este agendamento não pertence a este aluno.")

        # 2. Buscar pagamento
        payment = await self.payment_repository.get_by_scheduling_id(dto.scheduling_id)
        if payment is None:
            raise PaymentNotFoundException(f"para o agendamento {dto.scheduling_id}")

        # 3. Validar se pode disputar e marcar como disputed
        try:
            scheduling.mark_disputed()
        except ValueError as e:
            raise DomainException(str(e))

        # 4. Marcar pagamento como disputed
        try:
            payment.mark_disputed()
        except ValueError as e:
            raise DomainException(str(e))

        # 5. Salvar novos estados
        await self.scheduling_repository.update(scheduling)
        await self.payment_repository.update(payment)
