"""
Dispute SQLAlchemy Model

Modelo de banco de dados para disputas de aulas.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.dispute import Dispute
from src.domain.entities.dispute_enums import (
    DisputeReason,
    DisputeResolution,
    DisputeStatus,
)
from src.infrastructure.db.database import Base


class DisputeModel(Base):
    """
    Modelo SQLAlchemy para tabela de disputas.
    """

    __tablename__ = "disputes"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Keys
    scheduling_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("schedulings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    opened_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Dados da abertura
    reason: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    contact_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    contact_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Status e resolução
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )
    resolution: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )
    resolution_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    refund_type: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    # Relacionamentos
    scheduling = relationship("SchedulingModel", back_populates="dispute")
    opener = relationship(
        "UserModel",
        foreign_keys=[opened_by],
    )
    resolver = relationship(
        "UserModel",
        foreign_keys=[resolved_by],
    )

    def to_entity(self) -> Dispute:
        """Converte o modelo para entidade de domínio."""
        return Dispute(
            id=self.id,
            scheduling_id=self.scheduling_id,
            opened_by=self.opened_by,
            reason=DisputeReason(self.reason),
            description=self.description,
            contact_phone=self.contact_phone,
            contact_email=self.contact_email,
            status=DisputeStatus(self.status),
            resolution=DisputeResolution(self.resolution) if self.resolution else None,
            resolution_notes=self.resolution_notes,
            refund_type=self.refund_type,
            resolved_by=self.resolved_by,
            resolved_at=self.resolved_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, dispute: Dispute) -> "DisputeModel":
        """Cria modelo a partir de entidade de domínio."""
        return cls(
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
        )
