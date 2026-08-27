"""add intelligence and asset entities

Revision ID: f3a7d1c8b204
Revises: e2b6c9d8a103
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = "f3a7d1c8b204"
down_revision = "e2b6c9d8a103"
branch_labels = None
depends_on = None
U = lambda: postgresql.UUID(as_uuid=True)

def upgrade() -> None:
    op.create_table("assets", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("canonical_name", sa.String(255), nullable=False), sa.Column("asset_type", sa.String(48), nullable=False), sa.Column("criticality", sa.Integer(), server_default="0", nullable=False), sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("last_seen_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "canonical_name", name="uq_assets_tenant_name"))
    op.create_index("ix_assets_tenant_type", "assets", ["tenant_id", "asset_type"])
    op.create_table("vulnerabilities", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("cve", sa.String(32), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("severity", sa.String(16), nullable=False), sa.Column("cvss_score", sa.Integer()), sa.Column("description", sa.Text()), sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("vulnerability_instances", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("asset_id", U(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False), sa.Column("vulnerability_id", U(), sa.ForeignKey("vulnerabilities.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(24), server_default="open", nullable=False), sa.Column("evidence", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("resolved_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("tenant_id", "asset_id", "vulnerability_id", name="uq_vuln_instance_asset_vuln"))
    op.create_table("indicators", sa.Column("id", U(), primary_key=True), sa.Column("tenant_id", U(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False), sa.Column("indicator_type", sa.String(32), nullable=False), sa.Column("value", sa.String(512), nullable=False), sa.Column("verdict", sa.String(24)), sa.Column("confidence", sa.Integer()), sa.Column("source", sa.String(120)), sa.Column("metadata_json", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("tenant_id", "indicator_type", "value", name="uq_indicators_tenant_type_value"))

def downgrade() -> None:
    for table in ("indicators", "vulnerability_instances", "vulnerabilities", "assets"):
        op.drop_table(table)
