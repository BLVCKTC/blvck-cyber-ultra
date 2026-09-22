"""restore detection rule technique foreign keys

Revision ID: 7c6f6d09dd73
Revises: a4e8d37b3af4
Create Date: 2026-09-16 16:06:20.921233

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c6f6d09dd73'
down_revision: Union[str, None] = 'a4e8d37b3af4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    foreign_keys = {
        fk["name"]
        for fk in inspector.get_foreign_keys(
            "detection_rule_technique"
        )
    }

    if "fk_detection_rule_technique_detection_rule" not in foreign_keys:
        op.create_foreign_key(
            "fk_detection_rule_technique_detection_rule",
            "detection_rule_technique",
            "detection_rules",
            ["detection_rule_id"],
            ["id"],
            ondelete="CASCADE",
        )

    if "fk_detection_rule_technique_mitre_technique" not in foreign_keys:
        op.create_foreign_key(
            "fk_detection_rule_technique_mitre_technique",
            "detection_rule_technique",
            "mitre_technique",
            ["mitre_technique_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    if "fk_detection_rule_technique_created_by" not in foreign_keys:
        op.create_foreign_key(
            "fk_detection_rule_technique_created_by",
            "detection_rule_technique",
            "users",
            ["created_by"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    foreign_keys = {
        fk["name"]
        for fk in inspector.get_foreign_keys(
            "detection_rule_technique"
        )
    }

    if "fk_detection_rule_technique_created_by" in foreign_keys:
        op.drop_constraint(
            "fk_detection_rule_technique_created_by",
            "detection_rule_technique",
            type_="foreignkey",
        )

    if "fk_detection_rule_technique_mitre_technique" in foreign_keys:
        op.drop_constraint(
            "fk_detection_rule_technique_mitre_technique",
            "detection_rule_technique",
            type_="foreignkey",
        )

    if "fk_detection_rule_technique_detection_rule" in foreign_keys:
        op.drop_constraint(
            "fk_detection_rule_technique_detection_rule",
            "detection_rule_technique",
            type_="foreignkey",
        )