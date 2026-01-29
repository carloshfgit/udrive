"""criar_perfis_e_geolocalizacao

Revision ID: 2026012901
Revises: 
Create Date: 2026-01-29 08:50:00.000000

Cria tabelas de perfis de instrutores e alunos com suporte a PostGIS.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "2026012901"
down_revision: str | None = "5453ae9f3abf"  # Referencia migration de auth tables
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    # Habilitar extensão PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # Criar tabela instructor_profiles
    op.create_table(
        "instructor_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("vehicle_type", sa.String(100), nullable=False, server_default=""),
        sa.Column("license_category", sa.String(10), nullable=False, server_default="B"),
        sa.Column("hourly_rate", sa.Numeric(10, 2), nullable=False, server_default="80.00"),
        sa.Column("rating", sa.Numeric(3, 2), nullable=False, server_default="0.00"),
        sa.Column("total_reviews", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "location",
            Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id"),
    )

    # Criar índices para instructor_profiles
    op.create_index(
        "ix_instructor_profiles_user_id",
        "instructor_profiles",
        ["user_id"],
    )
    op.create_index(
        "ix_instructor_profiles_is_available",
        "instructor_profiles",
        ["is_available"],
    )
    op.create_index(
        "ix_instructor_profiles_location",
        "instructor_profiles",
        ["location"],
        postgresql_using="gist",
    )
    op.create_index(
        "ix_instructor_profiles_available_rating",
        "instructor_profiles",
        ["is_available", "rating"],
    )

    # Criar tabela student_profiles
    op.create_table(
        "student_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("preferred_schedule", sa.String(255), nullable=False, server_default=""),
        sa.Column("license_category_goal", sa.String(10), nullable=False, server_default="B"),
        sa.Column("learning_stage", sa.String(50), nullable=False, server_default="beginner"),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("total_lessons", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("user_id"),
    )

    # Criar índices para student_profiles
    op.create_index(
        "ix_student_profiles_user_id",
        "student_profiles",
        ["user_id"],
    )
    op.create_index(
        "ix_student_profiles_learning_stage",
        "student_profiles",
        ["learning_stage"],
    )


def downgrade() -> None:
    """Reverte a migration."""
    # Remover tabela student_profiles
    op.drop_index("ix_student_profiles_learning_stage", table_name="student_profiles")
    op.drop_index("ix_student_profiles_user_id", table_name="student_profiles")
    op.drop_table("student_profiles")

    # Remover tabela instructor_profiles
    op.drop_index("ix_instructor_profiles_available_rating", table_name="instructor_profiles")
    op.drop_index("ix_instructor_profiles_location", table_name="instructor_profiles")
    op.drop_index("ix_instructor_profiles_is_available", table_name="instructor_profiles")
    op.drop_index("ix_instructor_profiles_user_id", table_name="instructor_profiles")
    op.drop_table("instructor_profiles")

    # Nota: Não removemos a extensão PostGIS pois pode ser usada em outras tabelas
