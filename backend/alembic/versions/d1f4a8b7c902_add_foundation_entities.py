"""add foundation entities

Revision ID: d1f4a8b7c902
Revises: 05cd575b1582
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "d1f4a8b7c902"
down_revision = "05cd575b1582"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("teams", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("slug", sa.String(120), nullable=False), sa.Column("description", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "slug", name="uq_teams_tenant_slug"))
    op.create_index("ix_teams_tenant", "teams", ["tenant_id"])
    op.create_table("team_members", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(32), server_default="member", nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"))
    op.create_table("api_keys", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("key_prefix", sa.String(16), nullable=False), sa.Column("key_hash", sa.String(128), nullable=False), sa.Column("scopes", postgresql.JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False), sa.Column("last_used_at", sa.DateTime(timezone=True)), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "key_hash", name="uq_api_keys_tenant_hash"))
    op.create_index("ix_api_keys_tenant_active", "api_keys", ["tenant_id", "revoked_at"])
    op.create_table("security_settings", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True), sa.Column("mfa_required", sa.Boolean(), server_default=sa.text("false"), nullable=False), sa.Column("session_timeout_minutes", sa.Integer(), server_default="480", nullable=False), sa.Column("settings", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("audit_log_entries", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("action", sa.String(120), nullable=False), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", postgresql.UUID(as_uuid=True)), sa.Column("payload", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_audit_log_tenant_created", "audit_log_entries", ["tenant_id", "created_at"])
    op.create_table("plans", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("key", sa.String(40), unique=True, nullable=False), sa.Column("name", sa.String(80), nullable=False), sa.Column("limits", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False))
    op.create_table("subscriptions", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False), sa.Column("status", sa.String(24), server_default="trialing", nullable=False), sa.Column("current_period_end", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", name="uq_subscriptions_tenant"))
    op.create_table("domains", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("hostname", sa.String(255), nullable=False), sa.Column("verified_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "hostname", name="uq_domains_tenant_hostname"))
    op.create_table("organization_profiles", sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), primary_key=True), sa.Column("legal_name", sa.String(255)), sa.Column("industry", sa.String(120)), sa.Column("country", sa.String(2)), sa.Column("metadata_json", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    for table in ("organization_profiles", "domains", "subscriptions", "plans", "audit_log_entries", "security_settings", "api_keys", "team_members", "teams"):
        op.drop_table(table)
