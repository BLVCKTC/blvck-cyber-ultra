"""fix nullif guard and close rls gap on remaining tables

Revision ID: 61338bb0b6d7
Revises: 612a92fd2869
Create Date: 2026-09-02 12:46:04.089767

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61338bb0b6d7'
down_revision: Union[str, None] = '612a92fd2869'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── Part 1: fixing the 8 existing policies — ALTER POLICY, no drop needed ──

def upgrade() -> None:
    op.execute("""
        ALTER POLICY tenant_isolation_alerts ON alerts
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_detection_rules ON detection_rules
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_evidence ON evidence
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_investigations ON investigations
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_security_events ON security_events
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_teams ON teams
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY tenant_isolation_team_members ON team_members
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        ALTER POLICY membership_visibility ON memberships
        USING (
            user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
            OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
        WITH CHECK (
            tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
        )
    """)

    # ── Part 2: standard tenant-scoped tables — same policy shape, new tables ──

    STANDARD_TABLES = [
        "rule_versions", "detection_matches", "alert_feedback", "response_actions",
        "assets", "vulnerabilities", "vulnerability_instances", "indicators",
        "incidents", "incident_alerts",
        "api_keys", "domains", "security_settings", "subscriptions",
        "organization_profiles", "tenant_roles",
    ]
    for table in STANDARD_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
        """)

    # ── Part 3: tenant_role_permissions — no tenant_id column of its own,
    # scoped via its parent tenant_roles row instead ──

    op.execute("ALTER TABLE tenant_role_permissions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_role_permissions FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_role_permissions ON tenant_role_permissions")
    op.execute("""
        CREATE POLICY tenant_isolation_tenant_role_permissions ON tenant_role_permissions
        USING (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
        WITH CHECK (
            tenant_role_id IN (
                SELECT id FROM tenant_roles
                WHERE tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
            )
        )
    """)

    # ── Part 4: audit_log_entries — SELECT + INSERT only, deliberately no
    # UPDATE/DELETE policy at all. With FORCE RLS and zero permissive
    # policies for a command, that command is denied outright — this is
    # what makes the audit log actually append-only at the database level,
    # not just "not exposed via API." ──

    op.execute("ALTER TABLE audit_log_entries ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_log_entries FORCE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS audit_log_read ON audit_log_entries")
    op.execute("DROP POLICY IF EXISTS audit_log_insert ON audit_log_entries")
    op.execute("""
        CREATE POLICY audit_log_read ON audit_log_entries
        FOR SELECT
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)
    op.execute("""
        CREATE POLICY audit_log_insert ON audit_log_entries
        FOR INSERT
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)

    # ── Explicitly NOT touched, and why ──
    #
    # permissions, role_permissions, plans:
    #   Global catalog/reference data. No tenant_id column at all — same
    #   category as the MITRE reference tables. Never RLS.
    #
    # pkce_attempts:
    #   tenant_id is nullable by design ("allow tenant-less PKCE login
    #   attempts") and this table is read/written entirely within the
    #   /auth/login, /auth/callback flow — routes that only depend on
    #   get_db directly, before get_current_user or get_active_membership
    #   ever run. There is no tenant session context at all at that point
    #   in the request, not even an empty string. RLS here would either
    #   block the login flow outright or require threading tenant context
    #   through code that structurally runs before authentication exists.
    #   Left unprotected at the RLS layer by design, same category as
    #   users and tenants.


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS audit_log_insert ON audit_log_entries")
    op.execute("DROP POLICY IF EXISTS audit_log_read ON audit_log_entries")
    op.execute("ALTER TABLE audit_log_entries NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE audit_log_entries DISABLE ROW LEVEL SECURITY")

    op.execute("DROP POLICY IF EXISTS tenant_isolation_tenant_role_permissions ON tenant_role_permissions")
    op.execute("ALTER TABLE tenant_role_permissions NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_role_permissions DISABLE ROW LEVEL SECURITY")

    STANDARD_TABLES = [
        "rule_versions", "detection_matches", "alert_feedback", "response_actions",
        "assets", "vulnerabilities", "vulnerability_instances", "indicators",
        "incidents", "incident_alerts",
        "api_keys", "domains", "security_settings", "subscriptions",
        "organization_profiles", "tenant_roles",
    ]
    for table in STANDARD_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")

    # Revert Part 1 policies back to the unguarded version — included for
    # completeness, though reintroducing the bug on downgrade is obviously
    # not something you'd actually want to do.
    for table, policy in [
        ("alerts", "tenant_isolation_alerts"),
        ("detection_rules", "tenant_isolation_detection_rules"),
        ("evidence", "tenant_isolation_evidence"),
        ("investigations", "tenant_isolation_investigations"),
        ("security_events", "tenant_isolation_security_events"),
        ("teams", "tenant_isolation_teams"),
        ("team_members", "tenant_isolation_team_members"),
    ]:
        op.execute(f"""
            ALTER POLICY {policy} ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """)
    op.execute("""
        ALTER POLICY membership_visibility ON memberships
        USING (
            user_id = current_setting('app.user_id', true)::uuid
            OR tenant_id = current_setting('app.tenant_id', true)::uuid
        )
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
    """)