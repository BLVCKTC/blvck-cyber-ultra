from enum import Enum


class MembershipRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    SOC_MANAGER = "SOC_MANAGER"
    SOC_ANALYST = "SOC_ANALYST"
    INCIDENT_RESPONDER = "INCIDENT_RESPONDER"
    VIEWER = "VIEWER"