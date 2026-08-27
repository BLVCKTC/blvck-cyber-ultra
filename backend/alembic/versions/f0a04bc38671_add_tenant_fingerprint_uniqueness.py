"""add tenant fingerprint uniqueness

Revision ID: f0a04bc38671
Revises: 5ae7fee936eb
Create Date: 2026-08-26 10:55:18.637342

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f0a04bc38671"
down_revision: Union[str, None] = "5ae7fee936eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Enforce tenant-scoped uniqueness of security-event fingerprints.

    This provides the database-level guarantee required for
    race-condition-safe event deduplication.
    """
    op.create_unique_constraint(
        "uq_security_events_tenant_event_fingerprint",
        "security_events",
        ["tenant_id", "event_fingerprint"],
    )


def downgrade() -> None:
    """
    Remove the tenant-scoped fingerprint uniqueness constraint.
    """
    op.drop_constraint(
        "uq_security_events_tenant_event_fingerprint",
        "security_events",
        type_="unique",
    )