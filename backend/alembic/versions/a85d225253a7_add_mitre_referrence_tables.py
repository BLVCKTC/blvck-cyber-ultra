"""add_mitre_referrence_tables

Revision ID: a85d225253a7
Revises: 64ef4287edd5
Create Date: 2026-09-10 11:42:11.004976

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = 'a85d225253a7'
down_revision: Union[str, None] = '64ef4287edd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:

    mitre_domain = postgresql.ENUM(
    "enterprise-attack", "ics-attack", "mobile-attack", name="mitre_domain", create_type=False
    )
    mitre_domain.create(op.get_bind(), checkfirst=True)

    mitre_sync_status = postgresql.ENUM(
    "running", "success", "failed", name="mitre_sync_status", create_type=False
    )
    mitre_sync_status.create(op.get_bind(), checkfirst=True)

    # -- mitre_tactic --------------------------------------------------
    op.create_table(
        "mitre_tactic",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("shortname", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_tactic_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_tactic_stix_id"),
    )
    op.create_index("ix_mitre_tactic_mitre_id", "mitre_tactic", ["mitre_id"])

    # -- mitre_technique -------------------------------------------------
    op.create_table(
        "mitre_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("is_subtechnique", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "parent_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("platforms", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("data_sources", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("detection_guidance", sa.Text(), nullable=True),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_technique_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_technique_stix_id"),
    )
    op.create_index("ix_mitre_technique_mitre_id", "mitre_technique", ["mitre_id"])

    # -- mitre_mitigation --------------------------------------------------
    op.create_table(
        "mitre_mitigation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_mitigation_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_mitigation_stix_id"),
    )

    # -- mitre_group --------------------------------------------------
    op.create_table(
        "mitre_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_group_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_group_stix_id"),
    )

    # -- mitre_software --------------------------------------------------
    op.create_table(
        "mitre_software",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("aliases", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("software_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_software_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_software_stix_id"),
    )

    # -- mitre_campaign --------------------------------------------------
    op.create_table(
        "mitre_campaign",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mitre_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("stix_id", sa.String(128), nullable=False),
        sa.Column("deprecated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("mitre_id", "domain", name="uq_mitre_campaign_id_domain"),
        sa.UniqueConstraint("stix_id", name="uq_mitre_campaign_stix_id"),
    )

    # -- relationship / join tables --------------------------------------
    op.create_table(
        "mitre_technique_tactic",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_tactic_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_tactic.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("mitre_technique_id", "mitre_tactic_id", name="uq_technique_tactic"),
    )

    op.create_table(
        "mitre_technique_mitigation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_mitigation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_mitigation.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "mitre_technique_id", "mitre_mitigation_id", name="uq_technique_mitigation"
        ),
    )

    op.create_table(
        "mitre_group_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_group.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("mitre_group_id", "mitre_technique_id", name="uq_group_technique"),
    )

    op.create_table(
        "mitre_software_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_software_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_software.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "mitre_software_id", "mitre_technique_id", name="uq_software_technique"
        ),
    )

    op.create_table(
        "mitre_campaign_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_campaign.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "mitre_campaign_id", "mitre_technique_id", name="uq_campaign_technique"
        ),
    )

    op.create_table(
        "mitre_campaign_group",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "mitre_campaign_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_campaign.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_group.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint("mitre_campaign_id", "mitre_group_id", name="uq_campaign_group"),
    )

    # -- mitre_sync_log --------------------------------------------------
    op.create_table(
        "mitre_sync_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("domain", mitre_domain, nullable=False),
        sa.Column("mitre_version", sa.String(32), nullable=True),
        sa.Column("source_url", sa.String(512), nullable=False),
        sa.Column("status", mitre_sync_status, nullable=False, server_default="running"),
        sa.Column("objects_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("objects_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("objects_deprecated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # -- detection_rule_technique (tenant-scoped bridge, RLS via owning rule) --
    op.create_table(
        "detection_rule_technique",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "detection_rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("detection_rules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "mitre_technique_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("mitre_technique.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint(
            "detection_rule_id", "mitre_technique_id", name="uq_rule_technique"
        ),
    )
    op.create_index(
        "ix_detection_rule_technique_rule_id", "detection_rule_technique", ["detection_rule_id"]
    )
    op.create_index(
        "ix_detection_rule_technique_technique_id",
        "detection_rule_technique",
        ["mitre_technique_id"],
    )

    op.execute("ALTER TABLE detection_rule_technique ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE detection_rule_technique FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY detection_rule_technique_tenant_isolation
        ON detection_rule_technique
        USING (
            EXISTS (
                SELECT 1 FROM detection_rules dr
                WHERE dr.id = detection_rule_technique.detection_rule_id
                  AND dr.tenant_id = current_setting('app.tenant_id')::uuid
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM detection_rules dr
                WHERE dr.id = detection_rule_technique.detection_rule_id
                  AND dr.tenant_id = current_setting('app.tenant_id')::uuid
            )
        )
        """
    )
    # NOTE: verify `current_setting('app.tenant_id')` matches the session
    # variable name your existing RLS policies use (check e.g. the policy
    # on rule_versions or security_event) — swap it here if different.

    # No RLS on mitre_tactic / mitre_technique / mitre_mitigation /
    # mitre_group / mitre_software / mitre_campaign / mitre_sync_log:
    # these are global reference data readable by every tenant.


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS detection_rule_technique_tenant_isolation ON detection_rule_technique")
    op.drop_table("detection_rule_technique")
    op.drop_table("mitre_sync_log")
    op.drop_table("mitre_campaign_group")
    op.drop_table("mitre_campaign_technique")
    op.drop_table("mitre_software_technique")
    op.drop_table("mitre_group_technique")
    op.drop_table("mitre_technique_mitigation")
    op.drop_table("mitre_technique_tactic")
    op.drop_table("mitre_campaign")
    op.drop_table("mitre_software")
    op.drop_table("mitre_group")
    op.drop_table("mitre_mitigation")
    op.drop_table("mitre_technique")
    op.drop_table("mitre_tactic")

    postgresql.ENUM(name="mitre_sync_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="mitre_domain").drop(op.get_bind(), checkfirst=True)
