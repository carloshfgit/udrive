"""add_mp_refund_id_to_payments

Revision ID: 65021c511c6f
Revises: 804229d529e4
Create Date: 2026-03-06 22:36:32.894790+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "65021c511c6f"
down_revision: str | None = "804229d529e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    """Adiciona coluna mp_refund_id à tabela payments."""
    op.add_column("payments", sa.Column("mp_refund_id", sa.String(), nullable=True))
    op.create_index(
        op.f("ix_payments_mp_refund_id"), "payments", ["mp_refund_id"], unique=False
    )
def downgrade() -> None:
    """Remove coluna mp_refund_id da tabela payments."""
    op.drop_index(op.f("ix_payments_mp_refund_id"), table_name="payments")
    op.drop_column("payments", "mp_refund_id")