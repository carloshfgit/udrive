"""create_reviews_table

Revision ID: a218349dcd9a
Revises: 30028398e8ad
Create Date: 2026-02-06 13:33:54.033527+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a218349dcd9a"
down_revision: str | None = "30028398e8ad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration para criar a tabela de avaliações."""
    op.create_table(
        "reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scheduling_id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("instructor_id", sa.UUID(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["instructor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scheduling_id"], ["schedulings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scheduling_id"),
    )
    
    # Índices para busca rápida
    op.create_index(
        "ix_reviews_instructor_id",
        "reviews",
        ["instructor_id"],
        unique=False,
    )
    op.create_index(
        "ix_reviews_student_id",
        "reviews",
        ["student_id"],
        unique=False,
    )


def downgrade() -> None:
    """Reverte a migration removendo a tabela de avaliações."""
    op.drop_index("ix_reviews_student_id", table_name="reviews")
    op.drop_index("ix_reviews_instructor_id", table_name="reviews")
    op.drop_table("reviews")
