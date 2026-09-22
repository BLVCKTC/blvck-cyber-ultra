"""drop duplicate foreign key constraints on detection_rule_technique

Revision ID: d4049eab274c
Revises: 2021bf035a52
Create Date: 2026-09-14 08:40:03.543588

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision: str = 'd4049eab274c'
down_revision: Union[str, None] = '2021bf035a52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # These duplicate the auto-named *_fkey constraints already created
    # by detection_rule_technique's original create_table (matching the
    # model's inline ForeignKey() declarations). Same columns, same
    # target tables, same ON DELETE behavior — purely redundant.
    op.drop_constraint("fk_detection_rule_technique_created_by", "detection_rule_technique", type_="foreignkey")
    op.drop_constraint("fk_detection_rule_technique_detection_rule", "detection_rule_technique", type_="foreignkey")
    op.drop_constraint("fk_detection_rule_technique_mitre_technique", "detection_rule_technique", type_="foreignkey")
 
 
def downgrade() -> None:
    op.create_foreign_key(
        "fk_detection_rule_technique_mitre_technique",
        "detection_rule_technique", "mitre_technique",
        ["mitre_technique_id"], ["id"], ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_detection_rule_technique_detection_rule",
        "detection_rule_technique", "detection_rules",
        ["detection_rule_id"], ["id"], ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_detection_rule_technique_created_by",
        "detection_rule_technique", "users",
        ["created_by"], ["id"], ondelete="SET NULL",
    )
 