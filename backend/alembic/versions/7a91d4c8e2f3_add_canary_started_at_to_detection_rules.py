"""add canary_started_at to detection_rules

Revision ID: 7a91d4c8e2f3
Revises: fc95643ed61c
Create Date: 2026-09-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision: str = "7a91d4c8e2f3"
down_revision: str | None = "fc95643ed61c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "detection_rules",
        sa.Column(
            "canary_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "detection_rules",
        "canary_started_at",
    )