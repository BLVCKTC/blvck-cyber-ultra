"""recreate memberships table

Revision ID: a767a6ea261c
Revises: b04c5da2d9e9
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision: str = "a767a6ea261c"
down_revision: Union[str, None] = "b04c5da2d9e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


membership_role = postgresql.ENUM(
    "OWNER",
    "ADMIN",
    "SOC_MANAGER",
    "SOC_ANALYST",
    "INCIDENT_RESPONDER",
    "VIEWER",
    name="membershiprole",
)


def upgrade() -> None:
    bind = op.get_bind()

    # -----------------------------------------------------
    # Drop old table (safe because it is empty)
    # -----------------------------------------------------

    op.drop_table("memberships")

    # -----------------------------------------------------
    # Create enum
    # -----------------------------------------------------

    membership_role.create(bind, checkfirst=True)

    # -----------------------------------------------------
    # Create new memberships table
    # -----------------------------------------------------

    op.create_table(
        "memberships",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(
                "users.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "tenant_id",
            sa.String(),
            sa.ForeignKey(
                "tenants.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),

        sa.Column(
            "role",
            membership_role,
            nullable=False,
        ),

        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # -----------------------------------------------------
    # Indexes
    # -----------------------------------------------------

    op.create_index(
        "ix_memberships_user_id",
        "memberships",
        ["user_id"],
    )

    op.create_index(
        "ix_memberships_tenant_id",
        "memberships",
        ["tenant_id"],
    )

    op.create_index(
        "ix_membership_user_tenant",
        "memberships",
        ["user_id", "tenant_id"],
        unique=True,
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_index("ix_membership_user_tenant", table_name="memberships")
    op.drop_index("ix_memberships_user_id", table_name="memberships")
    op.drop_index("ix_memberships_tenant_id", table_name="memberships")

    op.drop_table("memberships")

    membership_role.drop(bind, checkfirst=True)

    # Recreate original table

    op.create_table(
        "memberships",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),

        sa.Column(
            "tenant_id",
            sa.String(),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),

        sa.Column(
            "role",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),

        sa.UniqueConstraint(
            "user_id",
            "tenant_id",
            name="uq_membership_user_tenant",
        ),
    )