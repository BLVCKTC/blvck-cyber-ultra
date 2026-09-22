"""allow nullable mitre ids for stix identity

Revision ID: fa362d05c536
Revises: 9bb93c8c7c1e
Create Date: 2026-09-11 14:06:03.595967

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = 'fa362d05c536'
down_revision: Union[str, None] = '9bb93c8c7c1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in (
        "mitre_tactic",
        "mitre_technique",
        "mitre_mitigation",
        "mitre_group",
        "mitre_software",
        "mitre_campaign",
    ):
        op.execute(
            sa.text(
                f"""
                UPDATE {table}
                SET mitre_id = NULL
                WHERE BTRIM(mitre_id) = ''
                """
            )
        )

        op.alter_column(
            table,
            "mitre_id",
            existing_type=sa.String(length=20),
            nullable=True,
        )


def downgrade() -> None:
    for table in (
        "mitre_tactic",
        "mitre_technique",
        "mitre_mitigation",
        "mitre_group",
        "mitre_software",
        "mitre_campaign",
    ):
        op.alter_column(
            table,
            "mitre_id",
            existing_type=sa.String(length=20),
            nullable=False,
        )