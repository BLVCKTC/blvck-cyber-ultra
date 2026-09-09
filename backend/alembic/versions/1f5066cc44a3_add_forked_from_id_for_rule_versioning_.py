"""add forked_from_id for rule versioning-on-edit

Revision ID: 1f5066cc44a3
Revises: 4fb0c4c00dbc
Create Date: 2026-09-08 14:06:49.334202

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '1f5066cc44a3'
down_revision: Union[str, None] = '4fb0c4c00dbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "detection_rules",
        sa.Column(
            "forked_from_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("detection_rules.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_detection_rules_forked_from",
        "detection_rules",
        ["forked_from_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_detection_rules_forked_from", table_name="detection_rules")
    op.drop_column("detection_rules", "forked_from_id")