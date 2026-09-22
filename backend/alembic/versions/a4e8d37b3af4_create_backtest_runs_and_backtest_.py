"""create backtest_runs and backtest_matches tables

Revision ID: a4e8d37b3af4
Revises: d4049eab274c
Create Date: 2026-09-14 09:22:58.191274

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'a4e8d37b3af4'
down_revision: Union[str, None] = 'd4049eab274c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "backtest_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detection_rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("detection_rules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'running'")),
        sa.Column("total_candidates", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("error_message", sa.Text()),
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_backtest_runs_tenant_rule", "backtest_runs", ["tenant_id", "detection_rule_id"])
 
    op.execute("ALTER TABLE backtest_runs ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE backtest_runs FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_backtest_runs ON backtest_runs
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
 
    op.create_table(
        "backtest_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("backtest_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("group_key", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("event_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_backtest_matches_run", "backtest_matches", ["backtest_run_id"])
 
    op.execute("ALTER TABLE backtest_matches ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE backtest_matches FORCE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_backtest_matches ON backtest_matches
        USING (
            EXISTS (
                SELECT 1 FROM backtest_runs br
                WHERE br.id = backtest_matches.backtest_run_id
                AND br.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM backtest_runs br
                WHERE br.id = backtest_matches.backtest_run_id
                AND br.tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
    """)
 
 
def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_backtest_matches ON backtest_matches")
    op.drop_table("backtest_matches")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_backtest_runs ON backtest_runs")
    op.drop_table("backtest_runs")
 