"""
List Disputes Use Case

Caso de uso para listar disputas com filtros (uso do painel administrativo).
"""

from dataclasses import dataclass

from src.application.dtos.dispute_dtos import (
    DisputeListResponseDTO,
    DisputeResponseDTO,
    ListDisputesDTO,
)
from src.domain.entities.dispute_enums import DisputeStatus
from src.domain.interfaces.dispute_repository import IDisputeRepository


@dataclass
class ListDisputesUseCase:
    """
    Caso de uso para listar disputas com paginação e filtro por status.

    Utilizado pelo painel administrativo para visualizar disputas
    abertas, em análise ou resolvidas.
    """

    dispute_repository: IDisputeRepository

    async def execute(self, dto: ListDisputesDTO) -> DisputeListResponseDTO:
        """
        Lista disputas com filtros.

        Args:
            dto: Filtros e paginação.

        Returns:
            DisputeListResponseDTO com lista paginada de disputas.
        """
        # Converter status string para enum se fornecido
        status_filter = None
        if dto.status:
            status_filter = DisputeStatus(dto.status)

        disputes_data = await self.dispute_repository.list_enriched(
            status=status_filter,
            limit=dto.limit,
            offset=dto.offset,
        )

        total = await self.dispute_repository.count_by_status(
            status=status_filter,
        )

        dispute_dtos = [
            DisputeResponseDTO(
                id=d.id,
                scheduling_id=d.scheduling_id,
                opened_by=d.opened_by,
                reason=d.reason.value,
                description=d.description,
                contact_phone=d.contact_phone,
                contact_email=d.contact_email,
                status=d.status.value,
                resolution=d.resolution.value if d.resolution else None,
                resolution_notes=d.resolution_notes,
                refund_type=d.refund_type,
                resolved_by=d.resolved_by,
                resolved_at=d.resolved_at,
                created_at=d.created_at,
                updated_at=d.updated_at,
                student_name=student_name,
                instructor_name=instructor_name,
                scheduled_datetime=scheduled_datetime,
            )
            for d, student_name, instructor_name, scheduled_datetime in disputes_data
        ]

        return DisputeListResponseDTO(
            disputes=dispute_dtos,
            total_count=total,
            limit=dto.limit,
            offset=dto.offset,
            has_more=(dto.offset + dto.limit) < total,
        )
