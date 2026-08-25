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

        # Organization
        "organization.view",
        "organization.update",

        # Security Monitoring
        "security.dashboard.view",
        "security.events.view",

        # Security Settings
        "security.settings.view",
        "security.settings.update",
        "security.events.update",

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
    # CUSTOMER ADMIN
    # =====================================================
    "ADMIN": [

        # Tenant
        "tenant.view",
        "tenant.update",

        # Organization
        "organization.view",
        "organization.update",

        # Security Monitoring
        "security.dashboard.view",
        "security.events.view",
        "security.events.update",

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

        # Security Monitoring
        "security.dashboard.view",
        "security.events.view",
        "security.events.update",

        # Security
        "security.settings.view",

        # Access
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
        "incidents.assign",
        "incidents.close",

        # Assets
        "assets.view",
        "assets.update",

        # Vulnerabilities
        "vulnerabilities.view",
        "vulnerabilities.assign",
        "vulnerabilities.remediate",

        # Threat Intelligence
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

        # Security Monitoring
        "security.dashboard.view",
        "security.events.view",
        "security.events.update",

        # Alerts
        "alerts.view",
        "alerts.assign",

        # Incidents
        "incidents.view",
        "incidents.create",
        "incidents.update",

        # Assets
        "assets.view",

        # Vulnerabilities
        "vulnerabilities.view",

        # Threat Intelligence
        "threatintel.view",

        # Detection
        "detections.view",

        # Detection Analytics
        "detection.analytics.view",

        # Forensics
        "forensics.view",

        # Reports
        "reports.view",

        # AI
        "ai.assistant.use",
    ],


    # =====================================================
    # INCIDENT RESPONDER
    # =====================================================
    "INCIDENT_RESPONDER": [

        # Security Monitoring
        "security.events.view",
        "security.events.update",
        
        # Alerts
        "alerts.view",
        "alerts.close",

        # Incidents
        "incidents.view",
        "incidents.update",
        "incidents.close",

        # Assets
        "assets.view",

        # Forensics
        "forensics.view",

        # Reports
        "reports.view",

        # AI
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