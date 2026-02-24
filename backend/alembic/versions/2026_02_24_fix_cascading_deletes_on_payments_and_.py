"""fix_cascading_deletes_on_payments_and_transactions

Revision ID: 53a1473d67bb
Revises: 3d10179d9390
Create Date: 2026-02-24 14:38:47.883549+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "53a1473d67bb"
down_revision: str | None = "3d10179d9390"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # payments: remover constraint antiga e adicionar com cascade
    op.drop_constraint("payments_student_id_fkey", "payments", type_="foreignkey")
    op.drop_constraint("payments_instructor_id_fkey", "payments", type_="foreignkey")
    
    op.create_foreign_key(
        "payments_student_id_fkey",
        "payments", "users",
        ["student_id"], ["id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "payments_instructor_id_fkey",
        "payments", "users",
        ["instructor_id"], ["id"],
        ondelete="CASCADE"
    )

    # transactions: remover constraint antiga e adicionar com cascade
    op.drop_constraint("transactions_user_id_fkey", "transactions", type_="foreignkey")
    op.drop_constraint("transactions_payment_id_fkey", "transactions", type_="foreignkey")

    op.create_foreign_key(
        "transactions_user_id_fkey",
        "transactions", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "transactions_payment_id_fkey",
        "transactions", "payments",
        ["payment_id"], ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    """Reverte a migration."""
    # transactions: reverter para como era antes
    op.drop_constraint("transactions_user_id_fkey", "transactions", type_="foreignkey")
    op.drop_constraint("transactions_payment_id_fkey", "transactions", type_="foreignkey")

    op.create_foreign_key(
        "transactions_user_id_fkey",
        "transactions", "users",
        ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "transactions_payment_id_fkey",
        "transactions", "payments",
        ["payment_id"], ["id"]
    )

    # payments: reverter para como era antes
    op.drop_constraint("payments_student_id_fkey", "payments", type_="foreignkey")
    op.drop_constraint("payments_instructor_id_fkey", "payments", type_="foreignkey")
    
    op.create_foreign_key(
        "payments_student_id_fkey",
        "payments", "users",
        ["student_id"], ["id"]
    )
    op.create_foreign_key(
        "payments_instructor_id_fkey",
        "payments", "users",
        ["instructor_id"], ["id"]
    )
