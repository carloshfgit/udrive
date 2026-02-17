"""create_transactions_table

Revision ID: 5f2e67d8a9c0
Revises: 4f1e56d7a8b9
Create Date: 2026-02-17 09:15:00.000000+00:00
"""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5f2e67d8a9c0"
down_revision: str | None = "4f1e56d7a8b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # Create transactions table
    op.create_table(
        "transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payment_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "payment",
                "refund",
                "platform_fee",
                "instructor_payout",
                name="transactiontype",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("gateway_reference_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(op.f("ix_transactions_type"), "transactions", ["type"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_transactions_type"), table_name="transactions")
    op.drop_index(op.f("ix_transactions_id"), table_name="transactions")
    op.drop_table("transactions")
    sa.Enum(name="transactiontype").drop(op.get_bind(), checkfirst=True)
