from __future__ import annotations


TENANT_ROLES = [

    {
        "key": "OWNER",
        "name": "Owner",
        "description": "Full tenant ownership with complete access to security operations, administration and configuration.",
        "is_system": True,
        "is_default": False,
    },

    {
        "key": "ADMIN",
        "name": "Administrator",
        "description": "Customer administrator responsible for users, roles, security settings, integrations and organization management.",
        "is_system": True,
        "is_default": False,
    },

    {
        "key": "SOC_MANAGER",
        "name": "SOC Manager",
        "description": "Manages security operations, threat monitoring, incidents, investigations and SOC workflows.",
        "is_system": True,
        "is_default": False,
    },

    {
        "key": "SOC_ANALYST",
        "name": "SOC Analyst",
        "description": "Monitors alerts, investigates threats and performs security analysis.",
        "is_system": True,
        "is_default": True,
    },

    {
        "key": "INCIDENT_RESPONDER",
        "name": "Incident Responder",
        "description": "Handles incident investigation, containment and response activities.",
        "is_system": True,
        "is_default": False,
    },

    {
        "key": "VIEWER",
        "name": "Viewer",
        "description": "Read-only access to approved security information and reports.",
        "is_system": True,
        "is_default": False,
    },
]