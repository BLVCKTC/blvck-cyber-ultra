"""add_quarantined_events

Revision ID: 64ef4287edd5
Revises: 1f5066cc44a3
Create Date: 2026-09-09 14:41:30.872204

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '64ef4287edd5'
down_revision: Union[str, None] = '1f5066cc44a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quarantined_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=255), nullable=False),
        sa.Column("failure_stage", sa.String(length=32), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=False),
        sa.Column("partial_normalized", postgresql.JSONB(), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "quarantined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )

    op.create_index(
        "ix_quarantined_events_tenant_id",
        "quarantined_events",
        ["tenant_id"],
    )

    op.create_index(
        "ix_quarantined_events_tenant_unresolved",
        "quarantined_events",
        ["tenant_id", "resolved_at"],
    )

    # Admin-only access: no tenant-scoped SELECT policy is created here,
    # matching every other table in this codebase's RLS pattern where
    # access is denied by default until a policy grants it. Confirm this
    # matches how your other admin-only tables (if any exist yet) are
    # locked down, so quarantined_events isn't accidentally left open by
    # a different default than the rest of the schema.
    op.execute("ALTER TABLE quarantined_events ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    op.drop_index(
        "ix_quarantined_events_tenant_unresolved",
        table_name="quarantined_events",
    )
    op.drop_index(
        "ix_quarantined_events_tenant_id",
        table_name="quarantined_events",
    )
    op.drop_table("quarantined_events")