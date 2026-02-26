"""audit_events table

Revision ID: 002
Revises: 001
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.String(255), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("status", sa.String(64), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("failure_category", sa.String(128), nullable=True),
        sa.Column("prompt_hash", sa.String(64), nullable=True),
        sa.Column("prompt_length", sa.Integer(), nullable=True),
        sa.Column("prompt_flags", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_request_id"), "audit_events", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_events_request_id"), table_name="audit_events")
    op.drop_table("audit_events")
