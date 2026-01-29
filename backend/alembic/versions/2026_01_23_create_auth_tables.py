"""create_auth_tables

Revision ID: 5453ae9f3abf
Revises: 0001_initial_setup
Create Date: 2026-01-23 00:16:50.844238+00:00

Migration para recriar tabelas de autenticação com nova estrutura:
- users: UUID como PK, campos renomeados
- refresh_tokens: UUID como PK, token_hash em vez de token
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5453ae9f3abf"
down_revision: str | None = "0001_initial_setup"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration - Recria tabelas de autenticação."""
    # Dropar tabelas existentes em ordem (refresh_tokens depende de users)
    op.execute("DROP TABLE IF EXISTS refresh_tokens")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    # Dropar enum antigo
    op.execute("DROP TYPE IF EXISTS userrole")

    # === CRIAR TABELA USERS ===
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("user_type", sa.String(50), nullable=False, index=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Índices compostos
    op.create_index(
        "ix_users_email_is_active", "users", ["email", "is_active"], unique=False
    )
    op.create_index(
        "ix_users_user_type_is_active", "users", ["user_type", "is_active"], unique=False
    )

    # === CRIAR TABELA REFRESH_TOKENS ===
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("token_hash", sa.String(255), nullable=False, index=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Índices compostos
    op.create_index(
        "ix_refresh_tokens_user_id_is_revoked",
        "refresh_tokens",
        ["user_id", "is_revoked"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"], unique=False
    )


def downgrade() -> None:
    """Reverte a migration - Recria estrutura antiga."""
    # Dropar tabelas novas
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    # Recriar enum
    userrole = postgresql.ENUM("STUDENT", "INSTRUCTOR", "ADMIN", name="userrole")
    userrole.create(op.get_bind())

    # Recriar tabela users antiga
    op.create_table(
        "users",
        sa.Column(
            "id", sa.INTEGER(), autoincrement=True, primary_key=True, nullable=False
        ),
        sa.Column("name", sa.VARCHAR(length=100), nullable=False),
        sa.Column("email", sa.VARCHAR(), nullable=False),
        sa.Column("password_hash", sa.VARCHAR(), nullable=False),
        sa.Column("role", userrole, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Recriar tabela refresh_tokens antiga
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id", sa.INTEGER(), autoincrement=True, primary_key=True, nullable=False
        ),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("token", sa.VARCHAR(), nullable=False),
        sa.Column("expires_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("revoked", sa.BOOLEAN(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="refresh_tokens_user_id_fkey"
        ),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"], unique=False)
    op.create_index(
        "ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True
    )
