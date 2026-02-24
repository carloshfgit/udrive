"""
Payment Model

Modelo SQLAlchemy para a tabela 'payments'.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DECIMAL, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.payment import Payment
from src.domain.entities.payment_status import PaymentStatus
from src.infrastructure.db.database import Base


class PaymentModel(Base):
    """Modelo ORM para pagamentos."""

    __tablename__ = "payments"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True
    )
    scheduling_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("schedulings.id"), nullable=False, unique=True
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    instructor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    platform_fee_percentage: Mapped[float] = mapped_column(
        DECIMAL(5, 2), nullable=False
    )
    platform_fee_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    instructor_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="paymentstatus",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )
    preference_group_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    gateway_payment_id: Mapped[str | None] = mapped_column(nullable=True)
    gateway_preference_id: Mapped[str | None] = mapped_column(nullable=True)
    gateway_provider: Mapped[str] = mapped_column(nullable=False, default="mercadopago")
    payer_email: Mapped[str | None] = mapped_column(nullable=True)
    refund_amount: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=datetime.utcnow, nullable=True
    )

    # Relacionamentos
    student = relationship(
        "UserModel", foreign_keys=[student_id], back_populates="student_payments"
    )
    instructor = relationship(
        "UserModel",
        foreign_keys=[instructor_id],
        back_populates="instructor_payments",
    )
    scheduling = relationship("SchedulingModel", back_populates="payment")
    transactions = relationship(
        "TransactionModel",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    def to_entity(self) -> Payment:
        """Converte model para entidade de domínio."""
        return Payment(
            id=self.id,
            scheduling_id=self.scheduling_id,
            student_id=self.student_id,
            instructor_id=self.instructor_id,
            amount=self.amount,
            platform_fee_percentage=self.platform_fee_percentage,
            platform_fee_amount=self.platform_fee_amount,
            instructor_amount=self.instructor_amount,
            status=self.status,
            preference_group_id=self.preference_group_id,
            gateway_payment_id=self.gateway_payment_id,
            gateway_preference_id=self.gateway_preference_id,
            gateway_provider=self.gateway_provider,
            payer_email=self.payer_email,
            refund_amount=self.refund_amount,
            refunded_at=self.refunded_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: Payment) -> "PaymentModel":
        """Cria model a partir de entidade de domínio."""
        return cls(
            id=entity.id,
            scheduling_id=entity.scheduling_id,
            student_id=entity.student_id,
            instructor_id=entity.instructor_id,
            amount=entity.amount,
            platform_fee_percentage=entity.platform_fee_percentage,
            platform_fee_amount=entity.platform_fee_amount,
            instructor_amount=entity.instructor_amount,
            status=entity.status,
            preference_group_id=entity.preference_group_id,
            gateway_payment_id=entity.gateway_payment_id,
            gateway_preference_id=entity.gateway_preference_id,
            gateway_provider=entity.gateway_provider,
            payer_email=entity.payer_email,
            refund_amount=entity.refund_amount,
            refunded_at=entity.refunded_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
