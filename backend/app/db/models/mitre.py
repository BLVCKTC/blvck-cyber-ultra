import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MitreDomain(str, enum.Enum):
    ENTERPRISE = "enterprise-attack"
    ICS = "ics-attack"
    MOBILE = "mobile-attack"


class MitreSyncStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


def mitre_domain_enum() -> Enum:
    return Enum(
        MitreDomain,
        name="mitre_domain",
        values_callable=lambda enum_class: [member.value for member in enum_class],
    )


def mitre_sync_status_enum() -> Enum:
    return Enum(
        MitreSyncStatus,
        name="mitre_sync_status",
        values_callable=lambda enum_class: [member.value for member in enum_class],
    )


class MitreTactic(Base):
    __tablename__ = "mitre_tactic"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_tactic_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    shortname: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MitreTechnique(Base):
    __tablename__ = "mitre_technique"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_technique_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    is_subtechnique: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parent_technique_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="SET NULL"), nullable=True
    )
    platforms: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    data_sources: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    detection_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    parent: Mapped["MitreTechnique | None"] = relationship(remote_side=[id])


class MitreMitigation(Base):
    __tablename__ = "mitre_mitigation"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_mitigation_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MitreGroup(Base):
    __tablename__ = "mitre_group"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_group_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MitreSoftware(Base):
    __tablename__ = "mitre_software"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_software_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    software_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MitreCampaign(Base):
    __tablename__ = "mitre_campaign"
    __table_args__ = (
        UniqueConstraint("mitre_id", "domain", name="uq_mitre_campaign_id_domain"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    stix_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    deprecated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class MitreTechniqueTactic(Base):
    __tablename__ = "mitre_technique_tactic"
    __table_args__ = (
        UniqueConstraint("mitre_technique_id", "mitre_tactic_id", name="uq_technique_tactic"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False
    )
    mitre_tactic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_tactic.id", ondelete="CASCADE"), nullable=False
    )


class MitreTechniqueMitigation(Base):
    __tablename__ = "mitre_technique_mitigation"
    __table_args__ = (
        UniqueConstraint("mitre_technique_id", "mitre_mitigation_id", name="uq_technique_mitigation"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False
    )
    mitre_mitigation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_mitigation.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class MitreGroupTechnique(Base):
    __tablename__ = "mitre_group_technique"
    __table_args__ = (
        UniqueConstraint("mitre_group_id", "mitre_technique_id", name="uq_group_technique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_group.id", ondelete="CASCADE"), nullable=False
    )
    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class MitreSoftwareTechnique(Base):
    __tablename__ = "mitre_software_technique"
    __table_args__ = (
        UniqueConstraint("mitre_software_id", "mitre_technique_id", name="uq_software_technique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_software_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_software.id", ondelete="CASCADE"), nullable=False
    )
    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class MitreCampaignTechnique(Base):
    __tablename__ = "mitre_campaign_technique"
    __table_args__ = (
        UniqueConstraint("mitre_campaign_id", "mitre_technique_id", name="uq_campaign_technique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_campaign.id", ondelete="CASCADE"), nullable=False
    )
    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_technique.id", ondelete="RESTRICT"), nullable=False
    )


class MitreCampaignGroup(Base):
    __tablename__ = "mitre_campaign_group"
    __table_args__ = (
        UniqueConstraint("mitre_campaign_id", "mitre_group_id", name="uq_campaign_group"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mitre_campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_campaign.id", ondelete="CASCADE"), nullable=False
    )
    mitre_group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_group.id", ondelete="CASCADE"), nullable=False
    )


class MitreSyncLog(Base):
    __tablename__ = "mitre_sync_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain: Mapped[MitreDomain] = mapped_column(mitre_domain_enum(), nullable=False)
    mitre_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[MitreSyncStatus] = mapped_column(
        mitre_sync_status_enum(), nullable=False, default=MitreSyncStatus.RUNNING
    )
    objects_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    objects_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    objects_deprecated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DetectionRuleTechnique(Base):
    __tablename__ = "detection_rule_technique"
    __table_args__ = (
        UniqueConstraint(
            "detection_rule_id",
            "mitre_technique_id",
            name="uq_rule_technique",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    detection_rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "detection_rules.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    mitre_technique_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "mitre_technique.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    technique: Mapped["MitreTechnique"] = relationship()