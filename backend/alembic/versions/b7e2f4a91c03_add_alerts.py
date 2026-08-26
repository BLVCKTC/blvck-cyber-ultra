"""add alerts foundation

Revision ID: b7e2f4a91c03
Revises: 9c1d2e4f7a8b
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = 'b7e2f4a91c03'
down_revision = '9c1d2e4f7a8b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('detection_rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('detection_rules.id', ondelete='SET NULL')),
        sa.Column('security_event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('security_events.id', ondelete='SET NULL')),
        sa.Column('fingerprint', sa.String(128), nullable=False),
        sa.Column('title', sa.String(255), nullable=False), sa.Column('description', sa.Text()),
        sa.Column('severity', sa.String(16), nullable=False), sa.Column('status', sa.String(24), nullable=False, server_default='new'),
        sa.Column('confidence', sa.Integer()), sa.Column('risk_score', sa.Integer()), sa.Column('source', sa.String(255)),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint("severity IN ('info','low','medium','high','critical')", name='ck_alerts_severity'),
        sa.CheckConstraint("status IN ('new','open','acknowledged','investigating','resolved','suppressed','false_positive')", name='ck_alerts_status'),
        sa.CheckConstraint('risk_score >= 0 AND risk_score <= 100', name='ck_alerts_risk_score'),
        sa.UniqueConstraint('tenant_id', 'fingerprint', name='uq_alerts_tenant_fingerprint'))
    op.create_index('ix_alerts_tenant_status', 'alerts', ['tenant_id','status'])
    op.create_index('ix_alerts_tenant_severity', 'alerts', ['tenant_id','severity'])
    op.create_index('ix_alerts_tenant_updated', 'alerts', ['tenant_id','updated_at'])

def downgrade() -> None:
    op.drop_index('ix_alerts_tenant_updated', table_name='alerts')
    op.drop_index('ix_alerts_tenant_severity', table_name='alerts')
    op.drop_index('ix_alerts_tenant_status', table_name='alerts')
    op.drop_table('alerts')
