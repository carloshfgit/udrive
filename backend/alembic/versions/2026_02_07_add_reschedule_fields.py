"""add_reschedule_fields

Revision ID: eff6f94e7d98
Revises: 7d768a8b929e
Create Date: 2026-02-07 17:32:34.106457+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "eff6f94e7d98"
down_revision: str | None = "7d768a8b929e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # 1. Adiciona a coluna rescheduled_datetime à tabela schedulings
    op.add_column(
        "schedulings",
        sa.Column("rescheduled_datetime", sa.DateTime(timezone=True), nullable=True),
    )

    # 2. Adiciona o novo status 'reschedule_requested' ao enum no PostgreSQL
    # Nota: No Postgres, alterações de TYPE não podem rodar dentro de transações em algumas versões,
    # mas o Alembic costuma lidar bem com isso via op.execute.
    op.execute("ALTER TYPE scheduling_status_enum ADD VALUE 'reschedule_requested'")


def downgrade() -> None:
    """Reverte a migration."""
    # 1. Remove a coluna rescheduled_datetime
    op.drop_column("schedulings", "rescheduled_datetime")

    # Nota: O PostgreSQL não suporta facilmente a remoção de valores de um ENUM (DROP VALUE).
    # Para reverter completamente, seria necessário recriar o tipo ENUM, o que é arriscado.
    # Por isso, no downgrade apenas removemos a coluna; o valor no ENUM permanecerá lá, 
    # mas não será utilizado pelo código.
