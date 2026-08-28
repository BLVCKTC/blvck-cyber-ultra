"""finish operation integrity and audit immutability

Revision ID: f4a7b8c9d012
Revises: e2b6c9d8a103
"""
from alembic import op
import sqlalchemy as sa

revision = "f4a7b8c9d012"
down_revision = "e2b6c9d8a103"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_incident_alerts_tenant", "incident_alerts", ["tenant_id", "created_at"])
    op.create_index("ix_alert_feedback_tenant_created", "alert_feedback", ["tenant_id", "created_at"])
    op.create_index("ix_response_actions_tenant_status", "response_actions", ["tenant_id", "status", "created_at"])
    op.create_unique_constraint("uq_alert_feedback_actor", "alert_feedback", ["tenant_id", "alert_id", "user_id"])
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_audit_mutation() RETURNS trigger
    LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'audit log entries are append-only'; END; $$;
    """)
    op.execute("""
    CREATE TRIGGER audit_log_entries_append_only
    BEFORE UPDATE OR DELETE ON audit_log_entries
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_log_entries_append_only ON audit_log_entries")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_mutation()")
    op.drop_constraint("uq_alert_feedback_actor", "alert_feedback", type_="unique")
    op.drop_index("ix_response_actions_tenant_status", table_name="response_actions")
    op.drop_index("ix_alert_feedback_tenant_created", table_name="alert_feedback")
    op.drop_index("ix_incident_alerts_tenant", table_name="incident_alerts")
