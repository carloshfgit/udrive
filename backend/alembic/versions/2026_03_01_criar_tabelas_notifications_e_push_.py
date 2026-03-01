"""criar_tabelas_notifications_e_push_tokens

Revision ID: 4222a096fadc
Revises: 15e9acc2bb62
Create Date: 2026-03-01 16:52:24.866512+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4222a096fadc"
down_revision: str | None = "15e9acc2bb62"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration: cria tabelas notifications e push_tokens."""
    # Tabela de notificações
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=True),
        sa.Column("action_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índice simples para listagem paginada por usuário
    op.create_index(
        "ix_notifications_user_created",
        "notifications",
        ["user_id", "created_at"],
    )

    # Índice parcial para contagem de não-lidas (badge do sininho)
    # Apenas linhas WHERE is_read = FALSE são indexadas, mantendo o índice pequeno
    op.execute(
        """
        CREATE INDEX ix_notifications_user_unread
            ON notifications (user_id, created_at DESC)
            WHERE is_read = FALSE
        """
    )

    # Tabela de push tokens
    op.create_table(
        "push_tokens",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(255), nullable=False, unique=True),
        sa.Column("device_id", sa.String(255), nullable=True),
        sa.Column("platform", sa.String(10), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Índice para busca de tokens ativos por usuário
    op.execute(
        """
        CREATE INDEX ix_push_tokens_user_active
            ON push_tokens (user_id)
            WHERE is_active = TRUE
        """
    )


def downgrade() -> None:
    """Reverte a migration: remove tabelas notifications e push_tokens."""
    op.drop_table("push_tokens")
    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_index("ix_notifications_user_created", table_name="notifications")
    op.drop_table("notifications")