from __future__ import annotations


ROLE_PERMISSIONS: dict[str, list[str]] = {

    # =====================================================
    # PLATFORM OWNER
    # =====================================================
    "OWNER": [

        # Platform
        "platform.all",

        # Tenant
        "tenant.view",
        "tenant.update",
        "tenant.delete",

        # Security Settings
        "security.settings.view",
        "security.settings.update",

        # Users
        "users.view",
        "users.create",
        "users.update",
        "users.delete",

        # Teams
        "team.view",
        "team.invite",
        "team.remove",
        "team.roles.manage",

        # Access Control
        "access.policies.view",
        "access.policies.manage",

        # MFA
        "mfa.view",
        "mfa.manage",

        # Alerts
        "alerts.view",
        "alerts.assign",
        "alerts.close",
        "alerts.delete",

        # Incidents
        "incidents.view",
        "incidents.create",
        "incidents.update",
        "incidents.close",
        "incidents.delete",

        # Assets
        "assets.view",
        "assets.create",
        "assets.update",
        "assets.delete",

        # Vulnerabilities
        "vulnerabilities.view",
        "vulnerabilities.manage",

        # Threat Intelligence
        "threatintel.view",
        "threatintel.manage",

        # Detection
        "detections.view",
        "detections.create",
        "detections.update",
        "detections.delete",
        "detections.deploy",

        # Detection Engineering
        "detection.analytics.view",
        "detection.analytics.manage",
        "detection.automation.view",
        "detection.automation.manage",

        # Forensics
        "forensics.view",
        "forensics.manage",

        # Reports
        "reports.view",
        "reports.generate",
        "reports.export",

        # Integrations
        "integrations.view",
        "integrations.manage",

        # API
        "apikeys.view",
        "apikeys.create",
        "apikeys.revoke",

        # Audit
        "audit.view",
        "audit.export",

        # Compliance
        "compliance.view",
        "compliance.manage",

        # AI
        "ai.assistant.use",
        "ai.configuration.manage",
    ],


# =====================================================
# CUSTOMER ADMIN
# =====================================================
"ADMIN": [

    # Tenant
    "tenant.view",
    "tenant.update",

    # Organization
    "organization.view",
    "organization.update",

    # Security Settings
    "security.settings.view",
    "security.settings.update",

    # Users
    "users.view",
    "users.create",
    "users.update",
    "users.delete",

    # Team
    "team.view",
    "team.invite",
    "team.remove",
    "team.roles.manage",

    # Access Control
    "access.policies.view",
    "access.policies.manage",

    # MFA / Identity
    "mfa.view",
    "mfa.manage",
    "sessions.view",
    "sessions.revoke",

    # Alerts
    "alerts.view",
    "alerts.assign",
    "alerts.close",
    "alerts.delete",

    # Incidents
    "incidents.view",
    "incidents.create",
    "incidents.update",
    "incidents.assign",
    "incidents.close",
    "incidents.delete",

    # Assets
    "assets.view",
    "assets.create",
    "assets.update",
    "assets.delete",

    # Vulnerabilities
    "vulnerabilities.view",
    "vulnerabilities.assign",
    "vulnerabilities.remediate",

    # Threat Intel
    "threatintel.view",
    "threatintel.manage",

    # Detection
    "detections.view",
    "detections.create",
    "detections.update",
    "detections.delete",
    "detections.deploy",

    # Detection Engineering
    "detection.analytics.view",
    "detection.analytics.manage",
    "detection.automation.view",
    "detection.automation.manage",

    # Forensics
    "forensics.view",
    "forensics.manage",

    # Reports
    "reports.view",
    "reports.generate",
    "reports.export",

    # Compliance
    "compliance.view",
    "compliance.manage",

    # Integrations
    "integrations.view",
    "integrations.manage",

    # API
    "apikeys.view",
    "apikeys.create",
    "apikeys.revoke",

    # Audit
    "audit.view",
    "audit.export",

    # Notifications
    "notifications.view",
    "notifications.manage",

    # Billing
    "billing.view",
    "billing.manage",

    # AI
    "ai.assistant.use",
    "ai.configuration.manage",
],


    # =====================================================
    # SOC MANAGER
    # =====================================================
    "SOC_MANAGER": [

        # Security visibility
        "security.settings.view",

        # Access visibility
        "access.policies.view",
        "mfa.view",

        # Alerts
        "alerts.view",
        "alerts.assign",
        "alerts.close",

        # Incidents
        "incidents.view",
        "incidents.create",
        "incidents.update",
        "incidents.close",

        # Assets
        "assets.view",
        "assets.update",

        # Vulnerabilities
        "vulnerabilities.view",
        "vulnerabilities.manage",

        # Threat Intel
        "threatintel.view",
        "threatintel.manage",

        # Detection
        "detections.view",
        "detections.create",
        "detections.update",
        "detections.deploy",

        # Detection Engineering
        "detection.analytics.view",
        "detection.analytics.manage",
        "detection.automation.view",
        "detection.automation.manage",

        # Forensics
        "forensics.view",
        "forensics.manage",

        # Reports
        "reports.view",
        "reports.generate",
        "reports.export",

        # Audit
        "audit.view",

        # Compliance
        "compliance.view",

        # AI
        "ai.assistant.use",
    ],


    # =====================================================
    # SOC ANALYST
    # =====================================================
    "SOC_ANALYST": [

        "alerts.view",
        "alerts.assign",

        "incidents.view",
        "incidents.create",
        "incidents.update",

        "assets.view",

        "vulnerabilities.view",

        "threatintel.view",

        "detections.view",

        "detection.analytics.view",

        "forensics.view",

        "reports.view",

        "ai.assistant.use",
    ],


    # =====================================================
    # INCIDENT RESPONDER
    # =====================================================
    "INCIDENT_RESPONDER": [

        "alerts.view",
        "alerts.close",

        "incidents.view",
        "incidents.update",
        "incidents.close",

        "assets.view",

        "forensics.view",

        "reports.view",

        "ai.assistant.use",
    ],


    # =====================================================
    # VIEW ONLY
    # =====================================================
    "VIEWER": [

        "alerts.view",

        "incidents.view",

        "assets.view",

        "vulnerabilities.view",

        "threatintel.view",

        "detections.view",

        "forensics.view",

        "reports.view",

        "audit.view",

        "compliance.view",
    ],
}