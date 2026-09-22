"""create canary_matches table

Revision ID: fc95643ed61c
Revises: 7bfcf2cd9890
Create Date: 2026-09-17 13:27:25.478317

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'fc95643ed61c'
down_revision: Union[str, None] = '7bfcf2cd9890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


 
def upgrade() -> None:
    op.create_table(
        "canary_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detection_rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_key", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("event_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("matched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_canary_matches_tenant_rule", "canary_matches", ["tenant_id", "detection_rule_id"])
 
    op.execute("ALTER TABLE canary_matches ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE canary_matches FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_canary_matches ON canary_matches
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
 
 
def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_canary_matches ON canary_matches")
    op.drop_table("canary_matches")