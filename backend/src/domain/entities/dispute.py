"""
Dispute Entity

Entidade de domínio representando uma disputa aberta por um aluno
em relação a um agendamento de aula.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .dispute_enums import DisputeReason, DisputeResolution, DisputeStatus


@dataclass
class Dispute:
    """
    Entidade de disputa vinculada a um agendamento.

    Registra o motivo, descrição e contatos do aluno, além do
    histórico de resolução pelo suporte administrativo.

    Attributes:
        scheduling_id: ID do agendamento em disputa (FK para Scheduling).
        opened_by: ID do aluno que abriu a disputa (FK para User).
        reason: Motivo pré-definido da disputa.
        description: Descrição detalhada do ocorrido pelo aluno.
        contact_phone: Telefone de contato do aluno.
        contact_email: E-mail de contato do aluno.
        status: Estado atual da disputa (OPEN, UNDER_REVIEW, RESOLVED).
        resolution: Tipo de resolução aplicada (se resolvida).
        resolution_notes: Notas internas do administrador.
        refund_type: Tipo de reembolso ("full", "partial" ou None).
        resolved_by: ID do admin que resolveu (FK para User).
        resolved_at: Data/hora da resolução.
    """

    scheduling_id: UUID
    opened_by: UUID
    reason: DisputeReason
    description: str
    contact_phone: str
    contact_email: str
    status: DisputeStatus = DisputeStatus.OPEN
    resolution: DisputeResolution | None = None
    resolution_notes: str | None = None
    refund_type: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if not self.description or not self.description.strip():
            raise ValueError("Descrição da disputa é obrigatória.")
        if not self.contact_phone or not self.contact_phone.strip():
            raise ValueError("Telefone de contato é obrigatório.")
        if not self.contact_email or not self.contact_email.strip():
            raise ValueError("E-mail de contato é obrigatório.")

    def start_review(self) -> None:
        """
        Marca a disputa como em análise pelo suporte.

        Raises:
            ValueError: Se a disputa não está no status OPEN.
        """
        if self.status != DisputeStatus.OPEN:
            raise ValueError(
                f"Análise só pode ser iniciada em disputas abertas. Status atual: {self.status}"
            )

        self.status = DisputeStatus.UNDER_REVIEW
        self.updated_at = datetime.now(timezone.utc)

    def resolve(
        self,
        resolution: DisputeResolution,
        resolved_by: UUID,
        resolution_notes: str,
        refund_type: str | None = None,
    ) -> None:
        """
        Resolve a disputa com o veredito do administrador.

        Args:
            resolution: Tipo de resolução (favor instrutor, aluno ou reagendamento).
            resolved_by: ID do admin que está resolvendo.
            resolution_notes: Notas internas de auditoria.
            refund_type: Tipo de reembolso ("full", "partial" ou None).

        Raises:
            ValueError: Se a disputa já foi resolvida ou não está em análise.
        """
        if self.status == DisputeStatus.RESOLVED:
            raise ValueError("Disputa já foi resolvida.")

        if self.status not in (DisputeStatus.OPEN, DisputeStatus.UNDER_REVIEW):
            raise ValueError(
                f"Disputa não pode ser resolvida no status atual: {self.status}"
            )

        if not resolution_notes or not resolution_notes.strip():
            raise ValueError("Notas de resolução são obrigatórias.")

        if resolution == DisputeResolution.FAVOR_STUDENT and refund_type not in (
            "full",
            "partial",
        ):
            raise ValueError(
                "Tipo de reembolso ('full' ou 'partial') é obrigatório para resolução a favor do aluno."
            )

        self.status = DisputeStatus.RESOLVED
        self.resolution = resolution
        self.resolved_by = resolved_by
        self.resolution_notes = resolution_notes
        self.refund_type = refund_type
        self.resolved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @property
    def is_open(self) -> bool:
        """Verifica se a disputa está aberta."""
        return self.status == DisputeStatus.OPEN

    @property
    def is_under_review(self) -> bool:
        """Verifica se está em análise."""
        return self.status == DisputeStatus.UNDER_REVIEW

    @property
    def is_resolved(self) -> bool:
        """Verifica se foi resolvida."""
        return self.status == DisputeStatus.RESOLVED
