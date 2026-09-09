"""add rule governance fields

Revision ID: 4fb0c4c00dbc
Revises: 510abc096744
Create Date: 2026-09-08 11:44:04.026614

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql




# revision identifiers, used by Alembic.
revision: str = '4fb0c4c00dbc'
down_revision: Union[str, None] = '510abc096744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("detection_rules", sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column("detection_rules", sa.Column("reviewed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column("detection_rules", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("detection_rules", sa.Column("review_notes", sa.Text(), nullable=True))
    op.add_column("detection_rules", sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column("detection_rules", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("detection_rules", sa.Column("approval_notes", sa.Text(), nullable=True))
    op.create_index("ix_detection_rules_created_by", "detection_rules", ["created_by_id"])


def downgrade() -> None:
    op.drop_index("ix_detection_rules_created_by", table_name="detection_rules")
    for col in ("approval_notes", "approved_at", "approved_by_id", "review_notes", "reviewed_at", "reviewed_by_id", "created_by_id"):
        op.drop_column("detection_rules", col)