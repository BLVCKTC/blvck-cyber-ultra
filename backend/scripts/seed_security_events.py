from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.security_event import SecurityEvent


TENANTS = {
    "3ea2dc7e-c96f-45d5-8379-ab37092600de": {
        "name": "BLVCK CYBER",
        "slug": "blvck-cyber",
        "network": "10.10.10",
        "prefix": "BLVCK",
    },
    "aa536111-bbec-4a21-b33d-2b652b8a1a68": {
        "name": "Great Dyke Mining Corporation",
        "slug": "great-dyke-mining",
        "network": "10.20.10",
        "prefix": "GREATDYKE",
    },
    "23457a57-f02d-4e19-a4d1-014df01a447e": {
        "name": "Hwange Minerals & Resources",
        "slug": "hwange-minerals",
        "network": "10.30.10",
        "prefix": "HWANGE",
    },
    "6cb5142e-898d-4b05-80de-e58a0d7645f8": {
        "name": "Midlands Chrome Mining",
        "slug": "midlands-chrome",
        "network": "10.40.10",
        "prefix": "MIDLANDS",
    },
    "e21bcb88-7943-4549-912c-7a89d8a1e898": {
        "name": "Matabeleland Gold Resources",
        "slug": "matabeleland-gold",
        "network": "10.50.10",
        "prefix": "MATABELELAND",
    },
}


BASE_TIME = datetime(
    2026,
    8,
    20,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_event(
    *,
    tenant_id: str,
    tenant: dict,
    index: int,
    event_type: str,
    category: str,
    source: str,
    source_type: str,
    severity: str,
    status: str,
    action: str,
    risk_score: int,
    hostname: str,
    user: str | None,
    source_ip: str | None,
    destination_ip: str | None,
    source_port: int | None = None,
    destination_port: int | None = None,
    protocol: str | None = None,
    process_name: str | None = None,
    process_id: int | None = None,
    mitre_tactic: str | None = None,
    mitre_technique: str | None = None,
    mitre_technique_id: str | None = None,
    message: str = "",
    normalized_data: dict | None = None,
    raw_event: dict | None = None,
):
    event_time = BASE_TIME + timedelta(minutes=index * 7)

    source_event_id = (
        f"{tenant['slug']}-"
        f"{event_time.strftime('%Y%m%d%H%M%S')}-"
        f"{index:04d}"
    )

    fingerprint = f"{tenant['slug']}:{event_type}:{hostname}:{event_time.isoformat()}"

    correlation_id = (
        f"{tenant['slug']}-attack-chain-{(index % 3) + 1}"
    )

    return SecurityEvent(
        id=uuid4(),
        tenant_id=tenant_id,
        source_event_id=source_event_id,
        event_fingerprint=fingerprint,
        correlation_id=correlation_id,
        parent_event_id=None,

        event_time=event_time,
        ingested_at=event_time + timedelta(seconds=4),
        created_at=event_time + timedelta(seconds=5),

        schema_version=1,

        event_category=category,
        source=source,
        source_type=source_type,
        event_type=event_type,

        severity=severity,
        status=status,

        action=action,
        risk_score=risk_score,

        source_ip=source_ip,
        destination_ip=destination_ip,
        source_port=source_port,
        destination_port=destination_port,
        protocol=protocol,

        hostname=hostname,
        user_identifier=user,

        process_name=process_name,
        process_id=process_id,

        mitre_tactic=mitre_tactic,
        mitre_technique=mitre_technique,
        mitre_technique_id=mitre_technique_id,

        message=message,

        raw_event=raw_event or {},
        normalized_data=normalized_data or {},
        event_metadata={
            "tenant_name": tenant["name"],
            "tenant_slug": tenant["slug"],
            "generator": "BLVCK CYBER demo telemetry",
            "environment": "production",
            "mock": True,
        },
    )


def generate_events():
    events = []

    for tenant_id, tenant in TENANTS.items():

        n = tenant["network"]
        p = tenant["prefix"]

        definitions = [
            # 1
            dict(
                event_type="failed_login",
                category="authentication",
                source="windows-security",
                source_type="endpoint",
                severity="high",
                status="open",
                action="denied",
                risk_score=78,
                hostname=f"{p}-WORKSTATION-01",
                user="administrator",
                source_ip=f"{n}.50",
                destination_ip=None,
                message="Multiple failed authentication attempts detected.",
                mitre_tactic="Credential Access",
                mitre_technique="Brute Force",
                mitre_technique_id="T1110",
                raw_event={
                    "event_id": 4625,
                    "logon_type": 3,
                    "failure_count": 8,
                },
                normalized_data={
                    "authentication_failure": True,
                    "attempt_count": 8,
                    "account": "administrator",
                },
            ),

            # 2
            dict(
                event_type="successful_login",
                category="authentication",
                source="active-directory",
                source_type="identity",
                severity="low",
                status="processed",
                action="allowed",
                risk_score=18,
                hostname=f"{p}-DC-01",
                user="j.moyo",
                source_ip=f"{n}.51",
                destination_ip=f"{n}.10",
                message="Successful domain authentication.",
                raw_event={
                    "event_id": 4624,
                    "logon_type": 3,
                },
                normalized_data={
                    "authentication_success": True,
                },
            ),

            # 3
            dict(
                event_type="powershell_execution",
                category="process",
                source="windows-defender",
                source_type="endpoint",
                severity="high",
                status="processing",
                action="detected",
                risk_score=82,
                hostname=f"{p}-WORKSTATION-02",
                user="admin",
                source_ip=f"{n}.52",
                destination_ip=None,
                process_name="powershell.exe",
                process_id=4820,
                message="Encoded PowerShell command execution detected.",
                mitre_tactic="Execution",
                mitre_technique="PowerShell",
                mitre_technique_id="T1059.001",
                raw_event={
                    "process": "powershell.exe",
                    "encoded": True,
                },
                normalized_data={
                    "command_interpreter": "powershell",
                    "encoded_command": True,
                },
            ),

            # 4
            dict(
                event_type="port_scan",
                category="network",
                source="network-sensor",
                source_type="network",
                severity="medium",
                status="processed",
                action="detected",
                risk_score=61,
                hostname=f"{p}-FIREWALL-01",
                user=None,
                source_ip=f"{n}.99",
                destination_ip=f"{n}.20",
                source_port=51432,
                destination_port=445,
                protocol="TCP",
                message="Internal host scanned multiple SMB endpoints.",
                mitre_tactic="Discovery",
                mitre_technique="Network Service Scanning",
                mitre_technique_id="T1046",
                raw_event={
                    "ports_scanned": 48,
                    "protocol": "TCP",
                },
                normalized_data={
                    "scan_detected": True,
                    "target_service": "SMB",
                },
            ),

            # 5
            dict(
                event_type="malware_detected",
                category="malware",
                source="endpoint-protection",
                source_type="endpoint",
                severity="critical",
                status="processed",
                action="blocked",
                risk_score=96,
                hostname=f"{p}-ENGINEERING-01",
                user="s.ncube",
                source_ip=f"{n}.60",
                destination_ip=None,
                process_name="invoice_viewer.exe",
                process_id=7312,
                message="Malicious executable blocked by endpoint protection.",
                mitre_tactic="Execution",
                mitre_technique="User Execution",
                mitre_technique_id="T1204",
                raw_event={
                    "malware_family": "Generic.Trojan",
                    "action": "blocked",
                },
                normalized_data={
                    "malware": True,
                    "blocked": True,
                    "file_type": "exe",
                },
            ),

            # 6
            dict(
                event_type="privilege_escalation",
                category="privilege",
                source="windows-security",
                source_type="endpoint",
                severity="high",
                status="open",
                action="detected",
                risk_score=87,
                hostname=f"{p}-SERVER-01",
                user="svc_backup",
                source_ip=f"{n}.61",
                destination_ip=None,
                process_name="cmd.exe",
                process_id=6501,
                message="Service account attempted privileged operation.",
                mitre_tactic="Privilege Escalation",
                mitre_technique="Abuse Elevation Control Mechanism",
                mitre_technique_id="T1548",
                raw_event={
                    "privileged_operation": True,
                },
                normalized_data={
                    "privilege_escalation": True,
                    "service_account": True,
                },
            ),

            # 7
            dict(
                event_type="outbound_connection",
                category="network",
                source="firewall",
                source_type="network",
                severity="medium",
                status="processed",
                action="allowed",
                risk_score=44,
                hostname=f"{p}-SERVER-02",
                user="system",
                source_ip=f"{n}.62",
                destination_ip="185.199.108.153",
                source_port=51822,
                destination_port=443,
                protocol="TCP",
                message="Outbound HTTPS connection observed.",
                raw_event={
                    "destination_port": 443,
                    "tls": True,
                },
                normalized_data={
                    "network_direction": "outbound",
                    "protocol": "https",
                },
            ),

            # 8
            dict(
                event_type="file_access",
                category="data_access",
                source="file-server",
                source_type="server",
                severity="medium",
                status="processed",
                action="read",
                risk_score=48,
                hostname=f"{p}-FILESERVER-01",
                user="finance.user",
                source_ip=f"{n}.70",
                destination_ip=None,
                message="Large number of sensitive documents accessed.",
                mitre_tactic="Collection",
                mitre_technique="Data from Local System",
                mitre_technique_id="T1005",
                raw_event={
                    "files_accessed": 127,
                    "classification": "confidential",
                },
                normalized_data={
                    "sensitive_data": True,
                    "file_count": 127,
                },
            ),

            # 9
            dict(
                event_type="process_created",
                category="process",
                source="edr",
                source_type="endpoint",
                severity="low",
                status="processed",
                action="created",
                risk_score=21,
                hostname=f"{p}-WORKSTATION-03",
                user="operator",
                source_ip=f"{n}.71",
                destination_ip=None,
                process_name="chrome.exe",
                process_id=9104,
                message="New browser process created.",
                raw_event={
                    "parent_process": "explorer.exe",
                    "process": "chrome.exe",
                },
                normalized_data={
                    "process_creation": True,
                },
            ),

            # 10
            dict(
                event_type="suspicious_dns",
                category="network",
                source="dns-sensor",
                source_type="network",
                severity="high",
                status="open",
                action="detected",
                risk_score=76,
                hostname=f"{p}-WORKSTATION-04",
                user="operator",
                source_ip=f"{n}.72",
                destination_ip=None,
                destination_port=53,
                protocol="UDP",
                message="Suspicious DNS request detected.",
                mitre_tactic="Command and Control",
                mitre_technique="Application Layer Protocol",
                mitre_technique_id="T1071",
                raw_event={
                    "query": "cdn-update-check.example",
                    "type": "TXT",
                },
                normalized_data={
                    "dns_anomaly": True,
                    "query_type": "TXT",
                },
            ),
        ]

        for index, definition in enumerate(definitions, start=1):
            events.append(
                make_event(
                    tenant_id=tenant_id,
                    tenant=tenant,
                    index=index,
                    **definition,
                )
            )

    return events


def main():
    engine = create_engine(settings.DATABASE_URL)

    events = generate_events()

    with Session(engine) as db:
        db.add_all(events)
        db.commit()

    print(f"Inserted {len(events)} security events.")

    for tenant_id, tenant in TENANTS.items():
        print(f"  {tenant['name']}: 10 events")


if __name__ == "__main__":
    main()