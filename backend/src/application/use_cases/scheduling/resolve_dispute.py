"""
Resolve Dispute Use Case

Caso de uso para o administrador resolver uma disputa.
"""

import structlog
from dataclasses import dataclass

from src.application.dtos.dispute_dtos import DisputeResponseDTO, ResolveDisputeDTO
from src.domain.entities.dispute_enums import DisputeResolution
from src.domain.interfaces.dispute_repository import IDisputeRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository

logger = structlog.get_logger(__name__)


class DisputeNotFoundException(Exception):
    """Disputa não encontrada."""

    def __init__(self, dispute_id: str) -> None:
        super().__init__(f"Disputa não encontrada: {dispute_id}")
        self.dispute_id = dispute_id


@dataclass
class ResolveDisputeUseCase:
    """
    Caso de uso para resolver uma disputa pelo administrador.

    Regras:
        - A disputa deve existir e não estar resolvida.
        - O scheduling associado deve estar no status DISPUTED.
        - Conforme a resolução:
            FAVOR_INSTRUCTOR: scheduling -> COMPLETED, pagamento liberado.
            FAVOR_STUDENT: scheduling -> CANCELLED, reembolso disparado.
            RESCHEDULED: scheduling -> CONFIRMED com nova data.

    Fluxo:
        1. Buscar disputa e scheduling associado.
        2. Validar estado de ambos.
        3. Aplicar resolução na disputa e transição no scheduling.
        4. Persistir ambos.
        5. Retornar DisputeResponseDTO.

    Nota:
        O reembolso (Celery task) e liberação de pagamento devem ser
        orquestrados pela camada Interface após receber o resultado.
    """

    dispute_repository: IDisputeRepository
    scheduling_repository: ISchedulingRepository

    async def execute(self, dto: ResolveDisputeDTO) -> DisputeResponseDTO:
        """
        Executa a resolução da disputa.

        Args:
            dto: Dados da resolução.

        Returns:
            DisputeResponseDTO com dados da disputa resolvida.

        Raises:
            DisputeNotFoundException: Se a disputa não existir.
            ValueError: Se a disputa já foi resolvida ou dados inválidos.
        """
        # 1. Buscar disputa
        dispute = await self.dispute_repository.get_by_id(dto.dispute_id)
        if dispute is None:
            raise DisputeNotFoundException(str(dto.dispute_id))

        # 2. Buscar scheduling associado
        scheduling = await self.scheduling_repository.get_by_id(dispute.scheduling_id)
        if scheduling is None:
            raise ValueError(
                f"Agendamento associado não encontrado: {dispute.scheduling_id}"
            )

        # 3. Converter resolução para enum
        resolution = DisputeResolution(dto.resolution)

        # 4. Validar e aplicar resolução na disputa
        dispute.resolve(
            resolution=resolution,
            resolved_by=dto.admin_id,
            resolution_notes=dto.resolution_notes,
            refund_type=dto.refund_type,
        )

        # 5. Aplicar transição no scheduling conforme resolução
        if resolution == DisputeResolution.FAVOR_INSTRUCTOR:
            scheduling.resolve_dispute_favor_instructor()

        elif resolution == DisputeResolution.FAVOR_STUDENT:
            scheduling.resolve_dispute_favor_student()

        elif resolution == DisputeResolution.RESCHEDULED:
            if dto.new_datetime is None:
                raise ValueError(
                    "Nova data é obrigatória para resolução por reagendamento."
                )
            scheduling.resolve_dispute_reschedule(dto.new_datetime)

        # 6. Persistir
        await self.dispute_repository.update(dispute)
        await self.scheduling_repository.update(scheduling)

        logger.info(
            "dispute_resolved",
            dispute_id=str(dispute.id),
            scheduling_id=str(dispute.scheduling_id),
            resolution=resolution.value,
            resolved_by=str(dto.admin_id),
        )

        # 7. Retornar DTO
        return DisputeResponseDTO(
            id=dispute.id,
            scheduling_id=dispute.scheduling_id,
            opened_by=dispute.opened_by,
            reason=dispute.reason.value,
            description=dispute.description,
            contact_phone=dispute.contact_phone,
            contact_email=dispute.contact_email,
            status=dispute.status.value,
            resolution=dispute.resolution.value if dispute.resolution else None,
            resolution_notes=dispute.resolution_notes,
            refund_type=dispute.refund_type,
            resolved_by=dispute.resolved_by,
            resolved_at=dispute.resolved_at,
            created_at=dispute.created_at,
            updated_at=dispute.updated_at,
            scheduled_datetime=scheduling.scheduled_datetime,
        )
