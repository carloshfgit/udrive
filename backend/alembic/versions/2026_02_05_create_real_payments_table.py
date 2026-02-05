"""create_real_payments_table

Revision ID: 30028398e8ad
Revises: 7a3b8c9d0e1f
Create Date: 2026-02-05 02:41:29.596966+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "30028398e8ad"
down_revision: str | None = "7a3b8c9d0e1f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # Create PaymentStatus Enum
    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scheduling_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("instructor_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("platform_fee_percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("platform_fee_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("instructor_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "completed",
                "failed",
                "refunded",
                "partially_refunded",
                name="paymentstatus",
            ),
            nullable=False,
        ),
        sa.Column("stripe_payment_intent_id", sa.String(), nullable=True),
        sa.Column("stripe_transfer_id", sa.String(), nullable=True),
        sa.Column("refund_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("refunded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["instructor_id"], ["users.id"], ),
        sa.ForeignKeyConstraint(["scheduling_id"], ["schedulings.id"], ),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scheduling_id"),
    )
    op.create_index(op.f("ix_payments_id"), "payments", ["id"], unique=False)
    op.create_index(op.f("ix_payments_status"), "payments", ["status"], unique=False)


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_index(op.f("ix_payments_status"), table_name="payments")
    op.drop_index(op.f("ix_payments_id"), table_name="payments")
    op.drop_table("payments")
    sa.Enum(name="paymentstatus").drop(op.get_bind(), checkfirst=True)
