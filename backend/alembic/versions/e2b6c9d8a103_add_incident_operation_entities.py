"""add incident and operation entities

Revision ID: e2b6c9d8a103
Revises: d1f4a8b7c902
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e2b6c9d8a103"
down_revision = "d1f4a8b7c902"
branch_labels = None
depends_on = None
U = lambda: postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table("incidents", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("status", sa.String(24), server_default="open", nullable=False), sa.Column("severity", sa.String(16), nullable=False), sa.Column("owner_user_id", U(), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("summary", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_incidents_tenant_status", "incidents", ["tenant_id", "status"])
    op.create_table("incident_alerts", sa.Column("incident_id", U(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True), sa.Column("alert_id", U(), sa.ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("rule_versions", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("detection_rule_id", U(), sa.ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("definition", postgresql.JSONB(), nullable=False), sa.Column("created_by", U(), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("detection_rule_id", "version", name="uq_rule_versions_rule_version"))
    op.create_table("detection_matches", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("security_event_id", U(), sa.ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False), sa.Column("rule_version_id", U(), sa.ForeignKey("rule_versions.id", ondelete="RESTRICT"), nullable=False), sa.Column("match_data", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("matched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("alert_feedback", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("alert_id", U(), sa.ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", U(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("label", sa.String(32), nullable=False), sa.Column("comment", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("response_actions", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("incident_id", U(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False), sa.Column("requested_by", U(), sa.ForeignKey("users.id"), nullable=False), sa.Column("action_type", sa.String(64), nullable=False), sa.Column("status", sa.String(24), server_default="pending_approval", nullable=False), sa.Column("parameters", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("approved_by", U(), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("executed_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    for table in ("response_actions", "alert_feedback", "detection_matches", "rule_versions", "incident_alerts", "incidents"):
        op.drop_table(table)
