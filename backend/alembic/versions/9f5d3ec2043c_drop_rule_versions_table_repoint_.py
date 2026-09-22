"""drop rule_versions table, repoint detection_matches to detection_rules

Revision ID: 9f5d3ec2043c
Revises: a85d225253a7
Create Date: 2026-09-11
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9f5d3ec2043c"
down_revision = "a85d225253a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # rule_versions was a parallel, unused versioning model — the real
    # version history is DetectionRule.forked_from_id (a fork chain),
    # enforced by RuleLockedError once a rule leaves DRAFT. Confirmed
    # empty in both tables before this migration; no data to preserve.

    # 1. Repoint detection_matches BEFORE touching rule_versions — the
    #    old FK constraint on rule_version_id is what blocks the drop
    #    if this order is reversed.
    op.drop_column("detection_matches", "rule_version_id")
    op.add_column(
        "detection_matches",
        sa.Column(
            "detection_rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("detection_rules.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_detection_matches_detection_rule_id",
        "detection_matches",
        ["detection_rule_id"],
    )

    # 2. Now nothing references rule_versions — safe to drop.
    op.execute("DROP POLICY IF EXISTS tenant_isolation_rule_versions ON rule_versions")
    op.execute("ALTER TABLE rule_versions NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE rule_versions DISABLE ROW LEVEL SECURITY")
    op.drop_table("rule_versions")


def downgrade() -> None:
    # Recreate rule_versions first, since the FK on rule_version_id
    # (restored below) needs it to exist.
    op.create_table(
        "rule_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detection_rule_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("definition", postgresql.JSONB(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("detection_rule_id", "version", name="uq_rule_versions_rule_version"),
    )
    op.execute("ALTER TABLE rule_versions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE rule_versions FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_rule_versions ON rule_versions
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)

    op.drop_index("ix_detection_matches_detection_rule_id", table_name="detection_matches")
    op.drop_column("detection_matches", "detection_rule_id")
    op.add_column(
        "detection_matches",
        sa.Column(
            "rule_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rule_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )