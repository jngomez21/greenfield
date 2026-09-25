"""Crea la tabla tasks (gestion-tareas, design.md § Modelo de datos).

Revision ID: 0001
Revises:
Create Date: 2026-09-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("owner_sub", sa.Text(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000)),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("due_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("btrim(title) <> ''", name="ck_tasks_title_not_blank"),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')", name="ck_tasks_status"
        ),
    )
    op.create_index(
        "ix_tasks_owner_created",
        "tasks",
        ["owner_sub", sa.text("created_at DESC"), sa.text("id DESC")],
    )
    op.create_index(
        "ix_tasks_owner_pending",
        "tasks",
        ["owner_sub", "due_date", "created_at", "id"],
        postgresql_where=sa.text("status <> 'completed'"),
    )


def downgrade() -> None:
    op.drop_table("tasks")
