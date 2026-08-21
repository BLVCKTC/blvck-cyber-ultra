"""add status to security events

Revision ID: 7a2c4d6e8f10
Revises: 515d231d0dc5
"""

from alembic import op
import sqlalchemy as sa


revision = "7a2c4d6e8f10"
down_revision = "515d231d0dc5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "security_events",
        sa.Column("status", sa.String(length=50), server_default="open", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("security_events", "status")
