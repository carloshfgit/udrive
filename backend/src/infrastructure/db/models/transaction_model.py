"""
Transaction Model

Modelo SQLAlchemy para a tabela 'transactions'.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DECIMAL, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.transaction import Transaction
from src.domain.entities.transaction_type import TransactionType
from src.infrastructure.db.database import Base


class TransactionModel(Base):
    """Modelo ORM para transações financeiras."""

    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True
    )
    payment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    stripe_reference_id: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relacionamentos
    payment = relationship("PaymentModel", back_populates="transactions")
    user = relationship("UserModel", back_populates="transactions")

    def to_entity(self) -> Transaction:
        """Converte model para entidade de domínio."""
        return Transaction(
            id=self.id,
            payment_id=self.payment_id,
            user_id=self.user_id,
            type=self.type,
            amount=self.amount,
            description=self.description,
            stripe_reference_id=self.stripe_reference_id,
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: Transaction) -> "TransactionModel":
        """Cria model a partir de entidade de domínio."""
        return cls(
            id=entity.id,
            payment_id=entity.payment_id,
            user_id=entity.user_id,
            type=entity.type,
            amount=entity.amount,
            description=entity.description,
            stripe_reference_id=entity.stripe_reference_id,
            created_at=entity.created_at,
        )
