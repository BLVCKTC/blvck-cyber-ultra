PERMISSIONS = [

    # =========================================================
    # PLATFORM (BLVCK CYBER OWNER / INTERNAL ADMIN)
    # =========================================================

    ("platform.all",
     "Platform Administrator",
     "Platform",
     "Full platform access",
     "critical"),

    ("platform.settings.view",
     "View Platform Settings",
     "Platform",
     "",
     "low"),

    ("platform.settings.edit",
     "Edit Platform Settings",
     "Platform",
     "",
     "critical"),


    # =========================================================
    # TENANT MANAGEMENT
    # =========================================================

    ("tenant.view",
     "View Tenant",
     "Tenant",
     "",
     "low"),

    ("tenant.update",
     "Update Tenant",
     "Tenant",
     "",
     "high"),

    ("tenant.delete",
     "Delete Tenant",
     "Tenant",
     "",
     "critical"),


    # =========================================================
    # ORGANIZATION PROFILE
    # =========================================================

    ("organization.view",
     "View Organization Profile",
     "Organization",
     "",
     "low"),

    ("organization.update",
     "Update Organization Profile",
     "Organization",
     "",
     "high"),


    # =========================================================
    # SECURITY SETTINGS
    # =========================================================

    ("security.settings.view",
     "View Security Settings",
     "Security",
     "",
     "low"),

    ("security.settings.update",
     "Update Security Settings",
     "Security",
     "",
     "critical"),


    # =========================================================
    # USERS
    # =========================================================

    ("users.view",
     "View Users",
     "Users",
     "",
     "low"),

    ("users.create",
     "Create Users",
     "Users",
     "",
     "medium"),

    ("users.update",
     "Update Users",
     "Users",
     "",
     "medium"),

    ("users.delete",
     "Delete Users",
     "Users",
     "",
     "critical"),


    # =========================================================
    # TEAMS
    # =========================================================

    ("team.view",
     "View Team",
     "Team",
     "",
     "low"),

    ("team.invite",
     "Invite Members",
     "Team",
     "",
     "medium"),

    ("team.remove",
     "Remove Members",
     "Team",
     "",
     "high"),

    ("team.roles.manage",
     "Manage Roles",
     "Team",
     "",
     "critical"),


    # =========================================================
    # ACCESS CONTROL
    # =========================================================

    ("access.policies.view",
     "View Access Policies",
     "Access Control",
     "",
     "low"),

    ("access.policies.manage",
     "Manage Access Policies",
     "Access Control",
     "",
     "high"),

    # =========================================================
    # MFA / IDENTITY SECURITY
    # =========================================================

    ("mfa.view",
     "View MFA Policies",
     "Authentication",
     "",
     "low"),

    ("mfa.manage",
     "Manage MFA Policies",
     "Authentication",
     "",
     "critical"),


    ("sessions.view",
     "View Active Sessions",
     "Authentication",
     "",
     "low"),

    ("sessions.revoke",
     "Revoke User Sessions",
     "Authentication",
     "",
     "high"),



    # =========================================================
    # ALERTS
    # =========================================================

    ("alerts.view",
     "View Alerts",
     "Alerts",
     "",
     "low"),

    ("alerts.assign",
     "Assign Alerts",
     "Alerts",
     "",
     "medium"),

    ("alerts.close",
     "Close Alerts",
     "Alerts",
     "",
     "medium"),

    ("alerts.delete",
     "Delete Alerts",
     "Alerts",
     "",
     "critical"),



    # =========================================================
    # INCIDENTS
    # =========================================================

    ("incidents.view",
     "View Incidents",
     "Incidents",
     "",
     "low"),

    ("incidents.create",
     "Create Incidents",
     "Incidents",
     "",
     "medium"),

    ("incidents.update",
     "Update Incidents",
     "Incidents",
     "",
     "medium"),

    ("incidents.assign",
     "Assign Incidents",
     "Incidents",
     "",
     "medium"),

    ("incidents.close",
     "Close Incidents",
     "Incidents",
     "",
     "high"),

    ("incidents.delete",
     "Delete Incidents",
     "Incidents",
     "",
     "critical"),



    # =========================================================
    # ASSETS
    # =========================================================

    ("assets.view",
     "View Assets",
     "Assets",
     "",
     "low"),

    ("assets.create",
     "Create Assets",
     "Assets",
     "",
     "medium"),

    ("assets.update",
     "Update Assets",
     "Assets",
     "",
     "medium"),

    ("assets.delete",
     "Delete Assets",
     "Assets",
     "",
     "high"),



    # =========================================================
    # VULNERABILITIES
    # =========================================================

    ("vulnerabilities.view",
     "View Vulnerabilities",
     "Vulnerabilities",
     "",
     "low"),

    ("vulnerabilities.assign",
     "Assign Vulnerabilities",
     "Vulnerabilities",
     "",
     "medium"),

    ("vulnerabilities.remediate",
     "Remediate Vulnerabilities",
     "Vulnerabilities",
     "",
     "high"),



    # =========================================================
    # THREAT INTELLIGENCE
    # =========================================================

    ("threatintel.view",
     "View Threat Intelligence",
     "Threat Intel",
     "",
     "low"),

    ("threatintel.manage",
     "Manage Threat Intelligence",
     "Threat Intel",
     "",
     "high"),



    # =========================================================
    # DETECTION ENGINEERING
    # =========================================================

    ("detections.view",
     "View Detection Rules",
     "Detection",
     "",
     "low"),

    ("detections.create",
     "Create Detection Rules",
     "Detection",
     "",
     "medium"),

    ("detections.update",
     "Update Detection Rules",
     "Detection",
     "",
     "high"),

    ("detections.delete",
     "Delete Detection Rules",
     "Detection",
     "",
     "critical"),

    ("detections.deploy",
     "Deploy Detection Rules",
     "Detection",
     "",
     "critical"),


    # Detection Analytics

    ("detection.analytics.view",
     "View Detection Analytics",
     "Detection",
     "",
     "low"),

    ("detection.analytics.manage",
     "Manage Detection Analytics",
     "Detection",
     "",
     "high"),


    # Detection Automation

    ("detection.automation.view",
     "View Detection Automation",
     "Detection",
     "",
     "low"),

    ("detection.automation.manage",
     "Manage Detection Automation",
     "Detection",
     "",
     "high"),

    # =========================================================
    # DIGITAL FORENSICS
    # =========================================================

    ("forensics.view",
     "View Forensics Cases",
     "Forensics",
     "",
     "low"),

    ("forensics.manage",
     "Manage Forensics Cases",
     "Forensics",
     "",
     "high"),



    # =========================================================
    # REPORTING
    # =========================================================

    ("reports.view",
     "View Reports",
     "Reports",
     "",
     "low"),

    ("reports.generate",
     "Generate Reports",
     "Reports",
     "",
     "medium"),

    ("reports.export",
     "Export Reports",
     "Reports",
     "",
     "medium"),



    # =========================================================
    # COMPLIANCE
    # =========================================================

    ("compliance.view",
     "View Compliance",
     "Compliance",
     "",
     "low"),

    ("compliance.manage",
     "Manage Compliance",
     "Compliance",
     "",
     "high"),



    # =========================================================
    # INTEGRATIONS
    # =========================================================

    ("integrations.view",
     "View Integrations",
     "Integrations",
     "",
     "low"),

    ("integrations.manage",
     "Manage Integrations",
     "Integrations",
     "",
     "high"),



    # =========================================================
    # API MANAGEMENT
    # =========================================================

    ("apikeys.view",
     "View API Keys",
     "API",
     "",
     "medium"),

    ("apikeys.create",
     "Create API Keys",
     "API",
     "",
     "high"),

    ("apikeys.revoke",
     "Revoke API Keys",
     "API",
     "",
     "critical"),



    # =========================================================
    # AUDIT
    # =========================================================

    ("audit.view",
     "View Audit Logs",
     "Audit",
     "",
     "medium"),

    ("audit.export",
     "Export Audit Logs",
     "Audit",
     "",
     "high"),



    # =========================================================
    # NOTIFICATIONS
    # =========================================================

    ("notifications.view",
     "View Notifications",
     "Notifications",
     "",
     "low"),

    ("notifications.manage",
     "Manage Notification Rules",
     "Notifications",
     "",
     "high"),



    # =========================================================
    # BILLING
    # =========================================================

    ("billing.view",
     "View Subscription",
     "Billing",
     "",
     "low"),

    ("billing.manage",
     "Manage Subscription",
     "Billing",
     "",
     "critical"),



    # =========================================================
    # AI
    # =========================================================

    ("ai.assistant.use",
     "Use AI Security Assistant",
     "AI",
     "",
     "low"),

    ("ai.configuration.manage",
     "Manage AI Configuration",
     "AI",
     "",
     "critical"),

         # =========================================================
    # SECURITY MONITORING
    # =========================================================

    ("security.dashboard.view",
     "View Security Dashboard",
     "Security",
     "",
     "low"),

    ("security.events.view",
     "View Security Events",
     "Security",
     "",
     "low"),

]