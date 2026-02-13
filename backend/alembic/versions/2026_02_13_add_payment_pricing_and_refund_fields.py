"""add_payment_pricing_and_refund_fields

Revision ID: 4f43612ea0c3
Revises: 2eb01092e3e0
Create Date: 2026-02-13 13:25:30.500715+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4f43612ea0c3"
down_revision: str | None = "2eb01092e3e0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # Payments: campos de precificação all-inclusive
    op.add_column(
        "payments",
        sa.Column("stripe_fee_amount", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "payments",
        sa.Column("total_student_amount", sa.Numeric(10, 2), nullable=True),
    )
    # Schedulings: trava de janela original pós-reagendamento
    op.add_column(
        "schedulings",
        sa.Column(
            "original_scheduled_datetime",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
def downgrade() -> None:
    """Reverte a migration."""
    op.drop_column("schedulings", "original_scheduled_datetime")
    op.drop_column("payments", "total_student_amount")
    op.drop_column("payments", "stripe_fee_amount")
