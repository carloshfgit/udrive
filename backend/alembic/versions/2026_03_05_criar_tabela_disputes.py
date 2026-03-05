"""criar_tabela_disputes

Revision ID: 295387644590
Revises: 9b4d2g6e3c8f
Create Date: 2026-03-05 18:03:36.679389+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "295387644590"
down_revision: str | None = "9b4d2g6e3c8f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.create_table(
        "disputes",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("scheduling_id", sa.UUID(), sa.ForeignKey("schedulings.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("opened_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolution", sa.String(30), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("refund_type", sa.String(10), nullable=True),
        sa.Column("resolved_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices para consultas frequentes
    op.create_index("ix_disputes_scheduling_id", "disputes", ["scheduling_id"])
    op.create_index("ix_disputes_status", "disputes", ["status"])
    op.create_index("ix_disputes_opened_by", "disputes", ["opened_by"])


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_index("ix_disputes_opened_by", table_name="disputes")
    op.drop_index("ix_disputes_status", table_name="disputes")
    op.drop_index("ix_disputes_scheduling_id", table_name="disputes")
    op.drop_table("disputes")
