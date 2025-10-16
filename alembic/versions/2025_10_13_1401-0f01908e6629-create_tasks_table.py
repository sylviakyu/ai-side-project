"""create tasks table

Revision ID: 0f01908e6629
Revises: 
Create Date: 2025-10-13 14:01:03.033294
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = "0f01908e6629"
down_revision = None
branch_labels = None
depends_on = None


TASK_STATUS_ENUM_NAME = "task_status"
TASK_STATUS_VALUES = ("PENDING", "PROCESSING", "DONE", "FAILED")


def upgrade() -> None:
    task_status_enum = sa.Enum(*TASK_STATUS_VALUES, name=TASK_STATUS_ENUM_NAME)
    task_status_enum.create(bind=op.get_bind(), checkfirst=True)

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            task_status_enum,
            nullable=False,
            server_default=sa.text(f"'{TASK_STATUS_VALUES[0]}'"),
        ),
        sa.Column(
            "created_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.DATETIME(fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("finished_at", mysql.DATETIME(fsp=6), nullable=True),
    )

    op.create_index("idx_tasks_status", "tasks", ["status"])


def downgrade() -> None:
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_table("tasks")

    task_status_enum = sa.Enum(*TASK_STATUS_VALUES, name=TASK_STATUS_ENUM_NAME)
    task_status_enum.drop(bind=op.get_bind(), checkfirst=True)
