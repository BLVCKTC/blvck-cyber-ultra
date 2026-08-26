"""add investigations and evidence
Revision ID: c8f3a5b19d27
Revises: b7e2f4a91c03
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision='c8f3a5b19d27'; down_revision='b7e2f4a91c03'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('investigations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('alert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alerts.id', ondelete='SET NULL')),
        sa.Column('title', sa.String(255), nullable=False), sa.Column('summary', sa.Text()),
        sa.Column('status', sa.String(24), server_default='open', nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.CheckConstraint("status IN ('open','investigating','resolved','closed')", name='ck_investigations_status'))
    op.create_index('ix_investigations_tenant_status','investigations',['tenant_id','status'])
    op.create_index('ix_investigations_tenant_updated','investigations',['tenant_id','updated_at'])
    op.create_table('evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('investigation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('investigations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evidence_type', sa.String(32), nullable=False), sa.Column('title', sa.String(255), nullable=False),
        sa.Column('reference', sa.String(512)), sa.Column('notes', sa.Text()),
        sa.Column('metadata_json', postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index('ix_evidence_tenant_investigation','evidence',['tenant_id','investigation_id'])
    op.create_index('ix_evidence_tenant_created','evidence',['tenant_id','created_at'])

def downgrade():
    op.drop_index('ix_evidence_tenant_created', table_name='evidence'); op.drop_index('ix_evidence_tenant_investigation', table_name='evidence'); op.drop_table('evidence')
    op.drop_index('ix_investigations_tenant_updated', table_name='investigations'); op.drop_index('ix_investigations_tenant_status', table_name='investigations'); op.drop_table('investigations')
