"""add detection rules

Revision ID: 9c1d2e4f7a8b
Revises: f678243ad1e5
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "9c1d2e4f7a8b"
down_revision = "f678243ad1e5"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("detection_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()),
        sa.Column("rule_type", sa.String(32), nullable=False), sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="draft"), sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")), sa.Column("query", sa.Text()),
        sa.Column("configuration", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("tags", postgresql.ARRAY(sa.String(100)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("mitre_technique_ids", postgresql.ARRAY(sa.String(50)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("mitre_tactic_ids", postgresql.ARRAY(sa.String(50)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("author", sa.String(255)), sa.Column("source", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("version > 0", name="ck_detection_rules_version_positive"),
        sa.CheckConstraint("rule_type IN ('threshold','query','correlation','behavioral','sigma')", name="ck_detection_rules_type"),
        sa.CheckConstraint("severity IN ('info','low','medium','high','critical')", name="ck_detection_rules_severity"),
        sa.CheckConstraint("status IN ('draft','testing','backtested','canary','approved','production','monitored','tuned','retired')", name="ck_detection_rules_status"),
    )
    for name, columns in [("ix_detection_rules_tenant", ["tenant_id"]),("ix_detection_rules_tenant_status",["tenant_id","status"]),("ix_detection_rules_tenant_enabled",["tenant_id","enabled"]),("ix_detection_rules_tenant_type",["tenant_id","rule_type"]),("ix_detection_rules_tenant_severity",["tenant_id","severity"])]: op.create_index(name, "detection_rules", columns)

def downgrade() -> None:
    for name in ["ix_detection_rules_tenant_severity","ix_detection_rules_tenant_type","ix_detection_rules_tenant_enabled","ix_detection_rules_tenant_status","ix_detection_rules_tenant"]: op.drop_index(name, table_name="detection_rules")
    op.drop_table("detection_rules")
