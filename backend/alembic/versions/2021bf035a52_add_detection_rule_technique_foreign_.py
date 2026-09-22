"""add detection rule technique foreign keys

Revision ID: 2021bf035a52
Revises: fa362d05c536
Create Date: 2026-09-11 14:45:06.582614

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = '2021bf035a52'
down_revision: Union[str, None] = 'fa362d05c536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_detection_rule_technique_detection_rule",
        "detection_rule_technique",
        "detection_rules",
        ["detection_rule_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_detection_rule_technique_mitre_technique",
        "detection_rule_technique",
        "mitre_technique",
        ["mitre_technique_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_detection_rule_technique_created_by",
        "detection_rule_technique",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_detection_rule_technique_created_by",
        "detection_rule_technique",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_detection_rule_technique_mitre_technique",
        "detection_rule_technique",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_detection_rule_technique_detection_rule",
        "detection_rule_technique",
        type_="foreignkey",
    )