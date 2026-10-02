"""partial unique index on evidence snapshot references

Closes the concurrent-run duplicate race: two orchestration runs could both
pass the in-code "already captured?" check and both insert. Rows with a NULL
reference (agent_summary) are excluded and unaffected.

Pre-flight (run 2 Oct 2026): no existing duplicates.

Revision ID: 9b3e7a41c2d8
Revises: 44c393f34ff4
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "9b3e7a41c2d8"
down_revision = "44c393f34ff4"
branch_labels = None
depends_on = None

INDEX_NAME = "uq_evidence_tenant_investigation_type_reference"


def upgrade() -> None:
    op.create_index(
        INDEX_NAME,
        "evidence",
        ["tenant_id", "investigation_id", "evidence_type", "reference"],
        unique=True,
        postgresql_where=sa.text("reference IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name="evidence")