"""remove duplicate detection rule technique foreign keys

Revision ID: 7bfcf2cd9890
Revises: 7c6f6d09dd73
Create Date: 2026-09-16 16:14:50.577362

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '7bfcf2cd9890'
down_revision: Union[str, None] = '7c6f6d09dd73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "detection_rule_technique_created_by_fkey",
        "detection_rule_technique",
        type_="foreignkey",
    )
    op.drop_constraint(
        "detection_rule_technique_detection_rule_id_fkey",
        "detection_rule_technique",
        type_="foreignkey",
    )
    op.drop_constraint(
        "detection_rule_technique_mitre_technique_id_fkey",
        "detection_rule_technique",
        type_="foreignkey",
    )


def downgrade() -> None:
    op.create_foreign_key(
        "detection_rule_technique_created_by_fkey",
        "detection_rule_technique",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "detection_rule_technique_detection_rule_id_fkey",
        "detection_rule_technique",
        "detection_rules",
        ["detection_rule_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "detection_rule_technique_mitre_technique_id_fkey",
        "detection_rule_technique",
        "mitre_technique",
        ["mitre_technique_id"],
        ["id"],
        ondelete="RESTRICT",
    )