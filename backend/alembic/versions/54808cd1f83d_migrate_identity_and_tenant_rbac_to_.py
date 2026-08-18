"""migrate identity and tenant RBAC to UUIDs

Revision ID: 54808cd1f83d
Revises: 4ebd48c80180
Create Date: 2026-08-18 15:10:08.623700

This migration converts application identity IDs to PostgreSQL UUIDs.

Converted:
    users.id
    tenants.id
    memberships.id
    memberships.user_id
    memberships.tenant_id
    memberships.tenant_role_id
    tenant_roles.id
    tenant_roles.tenant_id
    tenant_role_permissions.id
    tenant_role_permissions.tenant_role_id
    pkce_attempts.tenant_id

System permission IDs remain INTEGER because they are internal
catalog/template identifiers.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ---------------------------------------------------------------------------
# Alembic
# ---------------------------------------------------------------------------

revision: str = "54808cd1f83d"
down_revision: Union[str, None] = "4ebd48c80180"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _drop_fk_if_exists(
    conn,
    constraint_name: str,
    table_name: str,
) -> None:
    conn.execute(
        sa.text(
            f"""
            ALTER TABLE {table_name}
            DROP CONSTRAINT IF EXISTS {constraint_name}
            """
        )
    )


def upgrade() -> None:
    conn = op.get_bind()

    # PostgreSQL UUID generation.
    conn.execute(
        sa.text(
            """
            CREATE EXTENSION IF NOT EXISTS pgcrypto
            """
        )
    )

    # =======================================================================
    # 1. Create temporary UUID columns
    # =======================================================================

    # USERS
    op.add_column(
        "users",
        sa.Column(
            "_uuid",
            sa.UUID(),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    conn.execute(
        sa.text(
            """
            UPDATE users
            SET _uuid = gen_random_uuid()
            WHERE _uuid IS NULL
            """
        )
    )

    # TENANTS
    op.add_column(
        "tenants",
        sa.Column(
            "_uuid",
            sa.UUID(),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    conn.execute(
        sa.text(
            """
            UPDATE tenants
            SET _uuid = gen_random_uuid()
            WHERE _uuid IS NULL
            """
        )
    )

    # TENANT ROLES
    op.add_column(
        "tenant_roles",
        sa.Column(
            "_uuid",
            sa.UUID(),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    conn.execute(
        sa.text(
            """
            UPDATE tenant_roles
            SET _uuid = gen_random_uuid()
            WHERE _uuid IS NULL
            """
        )
    )

    # MEMBERSHIPS
    op.add_column(
        "memberships",
        sa.Column(
            "_uuid",
            sa.UUID(),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    conn.execute(
        sa.text(
            """
            UPDATE memberships
            SET _uuid = gen_random_uuid()
            WHERE _uuid IS NULL
            """
        )
    )

    # TENANT ROLE PERMISSIONS
    op.add_column(
        "tenant_role_permissions",
        sa.Column(
            "_uuid",
            sa.UUID(),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )

    conn.execute(
        sa.text(
            """
            UPDATE tenant_role_permissions
            SET _uuid = gen_random_uuid()
            WHERE _uuid IS NULL
            """
        )
    )

    # =======================================================================
    # 2. Create temporary FK UUID columns
    # =======================================================================

    # memberships.user_id
    op.add_column(
        "memberships",
        sa.Column(
            "_user_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # memberships.tenant_id
    op.add_column(
        "memberships",
        sa.Column(
            "_tenant_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # memberships.tenant_role_id
    op.add_column(
        "memberships",
        sa.Column(
            "_tenant_role_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # tenant_roles.tenant_id
    op.add_column(
        "tenant_roles",
        sa.Column(
            "_tenant_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # tenant_role_permissions.tenant_role_id
    op.add_column(
        "tenant_role_permissions",
        sa.Column(
            "_tenant_role_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # pkce_attempts.tenant_id
    op.add_column(
        "pkce_attempts",
        sa.Column(
            "_tenant_uuid",
            sa.UUID(),
            nullable=True,
        ),
    )

    # =======================================================================
    # 3. Populate UUID relationships
    # =======================================================================

    # memberships.user_id -> users._uuid
    conn.execute(
        sa.text(
            """
            UPDATE memberships m
            SET _user_uuid = u._uuid
            FROM users u
            WHERE m.user_id = u.id
            """
        )
    )

    # memberships.tenant_id -> tenants._uuid
    conn.execute(
        sa.text(
            """
            UPDATE memberships m
            SET _tenant_uuid = t._uuid
            FROM tenants t
            WHERE m.tenant_id = t.id
            """
        )
    )

    # memberships.tenant_role_id -> tenant_roles._uuid
    conn.execute(
        sa.text(
            """
            UPDATE memberships m
            SET _tenant_role_uuid = tr._uuid
            FROM tenant_roles tr
            WHERE m.tenant_role_id = tr.id
            """
        )
    )

    # tenant_roles.tenant_id -> tenants._uuid
    conn.execute(
        sa.text(
            """
            UPDATE tenant_roles tr
            SET _tenant_uuid = t._uuid
            FROM tenants t
            WHERE tr.tenant_id = t.id
            """
        )
    )

    # tenant_role_permissions.tenant_role_id -> tenant_roles._uuid
    conn.execute(
        sa.text(
            """
            UPDATE tenant_role_permissions trp
            SET _tenant_role_uuid = tr._uuid
            FROM tenant_roles tr
            WHERE trp.tenant_role_id = tr.id
            """
        )
    )

    # pkce_attempts.tenant_id -> tenants._uuid
    conn.execute(
        sa.text(
            """
            UPDATE pkce_attempts p
            SET _tenant_uuid = t._uuid
            FROM tenants t
            WHERE p.tenant_id = t.id
            """
        )
    )

    # =======================================================================
    # 4. Validate mappings BEFORE destructive changes
    # =======================================================================

    checks = [
        (
            "memberships.user_id",
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE _user_uuid IS NULL
            """,
        ),
        (
            "memberships.tenant_id",
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE _tenant_uuid IS NULL
            """,
        ),
        (
            "memberships.tenant_role_id",
            """
            SELECT COUNT(*)
            FROM memberships
            WHERE tenant_role_id IS NOT NULL
              AND _tenant_role_uuid IS NULL
            """,
        ),
        (
            "tenant_roles.tenant_id",
            """
            SELECT COUNT(*)
            FROM tenant_roles
            WHERE _tenant_uuid IS NULL
            """,
        ),
        (
            "tenant_role_permissions.tenant_role_id",
            """
            SELECT COUNT(*)
            FROM tenant_role_permissions
            WHERE _tenant_role_uuid IS NULL
            """,
        ),
        (
            "pkce_attempts.tenant_id",
            """
            SELECT COUNT(*)
            FROM pkce_attempts
            WHERE _tenant_uuid IS NULL
            """,
        ),
    ]

    for label, query in checks:
        count = conn.execute(sa.text(query)).scalar_one()

        if count != 0:
            raise RuntimeError(
                f"UUID migration validation failed for {label}: "
                f"{count} unmapped rows"
            )

    # =======================================================================
    # 5. Drop existing foreign keys
    # =======================================================================

    _drop_fk_if_exists(
        conn,
        "fk_membership_user",
        "memberships",
    )

    _drop_fk_if_exists(
        conn,
        "fk_membership_tenant",
        "memberships",
    )

    _drop_fk_if_exists(
        conn,
        "memberships_tenant_role_id_fkey",
        "memberships",
    )

    _drop_fk_if_exists(
        conn,
        "tenant_roles_tenant_id_fkey",
        "tenant_roles",
    )

    _drop_fk_if_exists(
        conn,
        "tenant_role_permissions_tenant_role_id_fkey",
        "tenant_role_permissions",
    )

    # =======================================================================
    # 6. Drop primary keys temporarily
    # =======================================================================

    _drop_fk_if_exists(
        conn,
        "users_pkey",
        "users",
    )

    _drop_fk_if_exists(
        conn,
        "tenants_pkey",
        "tenants",
    )

    _drop_fk_if_exists(
        conn,
        "memberships_pkey",
        "memberships",
    )

    _drop_fk_if_exists(
        conn,
        "tenant_roles_pkey",
        "tenant_roles",
    )

    _drop_fk_if_exists(
        conn,
        "tenant_role_permissions_pkey",
        "tenant_role_permissions",
    )




    # =======================================================================
    # Drop indexes that depend on the old FK columns
    # =======================================================================

    conn.execute(
        sa.text(
            """
            DROP INDEX IF EXISTS ix_memberships_user_id;
            DROP INDEX IF EXISTS ix_memberships_tenant_id;
            DROP INDEX IF EXISTS ix_memberships_tenant_role_id;
            DROP INDEX IF EXISTS ix_tenant_roles_tenant_id;
            DROP INDEX IF EXISTS ix_tenant_role_permissions_tenant_role_id;
            """
        )
    )


    # =======================================================================
    # 7. Replace primary key columns
    # =======================================================================

    op.drop_column("users", "id")

    op.alter_column(
        "users",
        "_uuid",
        new_column_name="id",
        nullable=False,
        server_default=None,
    )

    op.create_primary_key(
        "users_pkey",
        "users",
        ["id"],
    )

    # -----------------------------------------------------------------------

    op.drop_column("tenants", "id")

    op.alter_column(
        "tenants",
        "_uuid",
        new_column_name="id",
        nullable=False,
        server_default=None,
    )

    op.create_primary_key(
        "tenants_pkey",
        "tenants",
        ["id"],
    )

    # -----------------------------------------------------------------------

    op.drop_column("tenant_roles", "id")

    op.alter_column(
        "tenant_roles",
        "_uuid",
        new_column_name="id",
        nullable=False,
        server_default=None,
    )

    op.create_primary_key(
        "tenant_roles_pkey",
        "tenant_roles",
        ["id"],
    )

    # -----------------------------------------------------------------------

    op.drop_column("memberships", "id")

    op.alter_column(
        "memberships",
        "_uuid",
        new_column_name="id",
        nullable=False,
        server_default=None,
    )

    op.create_primary_key(
        "memberships_pkey",
        "memberships",
        ["id"],
    )

    # -----------------------------------------------------------------------

    op.drop_column(
        "tenant_role_permissions",
        "id",
    )

    op.alter_column(
        "tenant_role_permissions",
        "_uuid",
        new_column_name="id",
        nullable=False,
        server_default=None,
    )

    op.create_primary_key(
        "tenant_role_permissions_pkey",
        "tenant_role_permissions",
        ["id"],
    )

    # =======================================================================
    # 8. Replace FK columns
    # =======================================================================

    # memberships.user_id
    op.drop_column(
        "memberships",
        "user_id",
    )

    op.alter_column(
        "memberships",
        "_user_uuid",
        new_column_name="user_id",
        nullable=False,
    )

    # memberships.tenant_id
    op.drop_column(
        "memberships",
        "tenant_id",
    )

    op.alter_column(
        "memberships",
        "_tenant_uuid",
        new_column_name="tenant_id",
        nullable=False,
    )

    # memberships.tenant_role_id
    op.drop_column(
        "memberships",
        "tenant_role_id",
    )

    op.alter_column(
        "memberships",
        "_tenant_role_uuid",
        new_column_name="tenant_role_id",
        nullable=True,
    )

    # tenant_roles.tenant_id
    op.drop_column(
        "tenant_roles",
        "tenant_id",
    )

    op.alter_column(
        "tenant_roles",
        "_tenant_uuid",
        new_column_name="tenant_id",
        nullable=False,
    )

    # tenant_role_permissions.tenant_role_id
    op.drop_column(
        "tenant_role_permissions",
        "tenant_role_id",
    )

    op.alter_column(
        "tenant_role_permissions",
        "_tenant_role_uuid",
        new_column_name="tenant_role_id",
        nullable=False,
    )

    # pkce_attempts.tenant_id
    op.drop_column(
        "pkce_attempts",
        "tenant_id",
    )

    op.alter_column(
        "pkce_attempts",
        "_tenant_uuid",
        new_column_name="tenant_id",
        nullable=False,
    )

    # =======================================================================
    # 9. Recreate foreign keys
    # =======================================================================

    op.create_foreign_key(
        "fk_membership_user",
        "memberships",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_membership_tenant",
        "memberships",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "memberships_tenant_role_id_fkey",
        "memberships",
        "tenant_roles",
        ["tenant_role_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "tenant_roles_tenant_id_fkey",
        "tenant_roles",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "tenant_role_permissions_tenant_role_id_fkey",
        "tenant_role_permissions",
        "tenant_roles",
        ["tenant_role_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # NEW:
    # PKCE attempts now properly belong to a tenant.
    op.create_foreign_key(
        "pkce_attempts_tenant_id_fkey",
        "pkce_attempts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # =======================================================================
    # 10. Recreate indexes that depend on changed columns
    # =======================================================================

    # Existing indexes may have survived because PostgreSQL tracks
    # indexes by column identity, but explicitly ensure the important
    # tenant/user lookup indexes exist.

    op.create_index(
        "ix_memberships_user_id",
        "memberships",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_tenant_id",
        "memberships",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_tenant_role_id",
        "memberships",
        ["tenant_role_id"],
        unique=False,
    )

    op.create_index(
        "ix_tenant_roles_tenant_id",
        "tenant_roles",
        ["tenant_id"],
        unique=False,
    )

    op.create_index(
        "ix_tenant_role_permissions_tenant_role_id",
        "tenant_role_permissions",
        ["tenant_role_id"],
        unique=False,
    )

    # =======================================================================
    # 11. Final validation
    # =======================================================================

    validation = {
        "users": """
            SELECT COUNT(*) FROM users
        """,
        "tenants": """
            SELECT COUNT(*) FROM tenants
        """,
        "memberships": """
            SELECT COUNT(*) FROM memberships
        """,
        "tenant_roles": """
            SELECT COUNT(*) FROM tenant_roles
        """,
        "tenant_role_permissions": """
            SELECT COUNT(*) FROM tenant_role_permissions
        """,
        "pkce_attempts": """
            SELECT COUNT(*) FROM pkce_attempts
        """,
    }

    expected_counts = {
        "users": 5,
        "tenants": 1,
        "memberships": 5,
        "tenant_roles": 6,
        "tenant_role_permissions": None,
        "pkce_attempts": 12,
    }

    for table, query in validation.items():
        count = conn.execute(sa.text(query)).scalar_one()

        expected = expected_counts[table]

        if expected is not None and count != expected:
            raise RuntimeError(
                f"Post-migration validation failed for {table}: "
                f"expected {expected}, got {count}"
            )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade from UUID identity migration is intentionally disabled. "
        "Restore the pre-migration PostgreSQL backup instead."
    )