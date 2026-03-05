"""
Open Dispute Use Case

Caso de uso para o aluno abrir uma disputa em um agendamento.
"""

import structlog
from dataclasses import dataclass

from src.application.dtos.dispute_dtos import DisputeResponseDTO, OpenDisputeDTO
from src.domain.entities.dispute import Dispute
from src.domain.entities.dispute_enums import DisputeReason
from src.domain.exceptions import (
    SchedulingNotFoundException,
)
from src.domain.interfaces.dispute_repository import IDisputeRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository

logger = structlog.get_logger(__name__)


@dataclass
class OpenDisputeUseCase:
    """
    Caso de uso para abrir uma disputa referente a um agendamento.

    Regras:
        - O agendamento deve existir e pertencer ao aluno.
        - O agendamento deve estar no status CONFIRMED.
        - O horário de término da aula deve ter passado.
        - Não pode haver outra disputa aberta para o mesmo agendamento.

    Fluxo:
        1. Buscar agendamento por ID e validar propriedade.
        2. Chamar scheduling.open_dispute() (valida status e horário).
        3. Criar entidade Dispute com motivo, descrição e contatos.
        4. Persistir scheduling e dispute.
        5. Retornar DisputeResponseDTO.
    """

    scheduling_repository: ISchedulingRepository
    dispute_repository: IDisputeRepository

    async def execute(self, dto: OpenDisputeDTO) -> DisputeResponseDTO:
        """
        Executa a abertura de disputa.

        Args:
            dto: Dados da disputa a ser aberta.

        Returns:
            DisputeResponseDTO com dados da disputa criada.

        Raises:
            SchedulingNotFoundException: Se agendamento não existir.
            ValueError: Se o agendamento não pertencer ao aluno,
                já tiver disputa aberta, ou não puder ser disputado.
        """
        # 1. Buscar agendamento
        scheduling = await self.scheduling_repository.get_by_id(dto.scheduling_id)
        if scheduling is None:
            raise SchedulingNotFoundException(str(dto.scheduling_id))

        # 2. Validar que o aluno é dono do agendamento
        if scheduling.student_id != dto.student_id:
            raise ValueError("Acesso não autorizado a este agendamento.")

        # 3. Verificar se já existe disputa para este agendamento
        existing_dispute = await self.dispute_repository.get_by_scheduling_id(
            dto.scheduling_id
        )
        if existing_dispute is not None:
            raise ValueError("Já existe uma disputa para este agendamento.")

        # 4. Transição de status no scheduling (valida CONFIRMED + aula terminada)
        scheduling.open_dispute()

        # 5. Criar entidade Dispute
        reason = DisputeReason(dto.reason)
        dispute = Dispute(
            scheduling_id=dto.scheduling_id,
            opened_by=dto.student_id,
            reason=reason,
            description=dto.description,
            contact_phone=dto.contact_phone,
            contact_email=dto.contact_email,
        )

        # 6. Persistir
        await self.scheduling_repository.update(scheduling)
        created_dispute = await self.dispute_repository.create(dispute)

        logger.info(
            "dispute_opened",
            dispute_id=str(created_dispute.id),
            scheduling_id=str(dto.scheduling_id),
            reason=dto.reason,
        )

        # 7. Retornar DTO
        return DisputeResponseDTO(
            id=created_dispute.id,
            scheduling_id=created_dispute.scheduling_id,
            opened_by=created_dispute.opened_by,
            reason=created_dispute.reason.value,
            description=created_dispute.description,
            contact_phone=created_dispute.contact_phone,
            contact_email=created_dispute.contact_email,
            status=created_dispute.status.value,
            resolution=None,
            resolution_notes=None,
            refund_type=None,
            resolved_by=None,
            resolved_at=None,
            created_at=created_dispute.created_at,
            updated_at=created_dispute.updated_at,
            scheduled_datetime=scheduling.scheduled_datetime,
        )
