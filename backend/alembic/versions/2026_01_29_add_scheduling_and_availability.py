"""add_scheduling_and_availability

Revision ID: e27f6f8202c3
Revises: 2026012901
Create Date: 2026-01-29 14:20:44.237288+00:00

"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e27f6f8202c3"
down_revision: str | None = "2026012901"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create instructor_availability table
    op.create_table(
        "instructor_availability",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("instructor_id", sa.UUID(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["instructor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instructor_id",
            "day_of_week",
            "start_time",
            name="uq_instructor_availability_slot",
        ),
    )
    op.create_index(
        "ix_availability_day_time",
        "instructor_availability",
        ["day_of_week", "start_time"],
        unique=False,
    )
    op.create_index(
        "ix_availability_instructor",
        "instructor_availability",
        ["instructor_id"],
        unique=False,
    )

    # Create schedulings table
    # Enum type needs to be created if not exists
    # SQLAlchemy usually handles it inside create_table for Enum column
    
    op.create_table(
        "schedulings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("instructor_id", sa.UUID(), nullable=False),
        sa.Column("scheduled_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "cancelled",
                "completed",
                name="scheduling_status_enum",
            ),
            nullable=False,
        ),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("cancelled_by", sa.UUID(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["cancelled_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["instructor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_schedulings_created_at"), "schedulings", ["created_at"], unique=False
    )
    op.create_index(
        "ix_schedulings_instructor_date",
        "schedulings",
        ["instructor_id", "scheduled_datetime"],
        unique=False,
    )
    op.create_index("ix_schedulings_status", "schedulings", ["status"], unique=False)
    op.create_index(
        "ix_schedulings_student_date",
        "schedulings",
        ["student_id", "scheduled_datetime"],
        unique=False,
    )


def downgrade() -> None:
    # Drop schedulings
    op.drop_index("ix_schedulings_student_date", table_name="schedulings")
    op.drop_index("ix_schedulings_status", table_name="schedulings")
    op.drop_index("ix_schedulings_instructor_date", table_name="schedulings")
    op.drop_index(op.f("ix_schedulings_created_at"), table_name="schedulings")
    op.drop_table("schedulings")
    
    # Drop scheduling_status_enum type
    sa.Enum(name="scheduling_status_enum").drop(op.get_bind(), checkfirst=True)

    # Drop instructor_availability
    op.drop_index("ix_availability_instructor", table_name="instructor_availability")
    op.drop_index("ix_availability_day_time", table_name="instructor_availability")
    op.drop_table("instructor_availability")
