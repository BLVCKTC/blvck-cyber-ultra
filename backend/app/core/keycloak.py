from __future__ import annotations

"""
BLVCK CYBER — Keycloak Configuration

This module defines Keycloak endpoints and the OAuth2 scheme.
Authentication logic resides in app.api.deps, token verification 
in app.core.security.jwt_verify, and JWKS in app.core.security.jwks.

Do NOT implement get_current_user() in this module.
"""

from fastapi.security import OAuth2AuthorizationCodeBearer

from app.core.config import (
    KEYCLOAK_URL,
    KEYCLOAK_REALM,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_ISSUER,
    KEYCLOAK_ALLOWED_AUDIENCE,
)

# Base URLs
KEYCLOAK_REALM_URL = f"{KEYCLOAK_URL.rstrip('/')}/realms/{KEYCLOAK_REALM}"
OIDC_BASE = f"{KEYCLOAK_REALM_URL}/protocol/openid-connect"

# OIDC Endpoints
KEYCLOAK_AUTHORIZATION_URL = f"{OIDC_BASE}/auth"
KEYCLOAK_TOKEN_URL = f"{OIDC_BASE}/token"
KEYCLOAK_USERINFO_URL = f"{OIDC_BASE}/userinfo"
KEYCLOAK_LOGOUT_URL = f"{OIDC_BASE}/logout"
KEYCLOAK_CERTS_URL = f"{OIDC_BASE}/certs"

# OAuth2 Scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=KEYCLOAK_AUTHORIZATION_URL,
    tokenUrl=KEYCLOAK_TOKEN_URL,
)

__all__ = [
    "KEYCLOAK_URL",
    "KEYCLOAK_REALM",
    "KEYCLOAK_CLIENT_ID",
    "KEYCLOAK_CLIENT_SECRET",
    "KEYCLOAK_ISSUER",
    "KEYCLOAK_ALLOWED_AUDIENCE",
    "KEYCLOAK_REALM_URL",
    "KEYCLOAK_AUTHORIZATION_URL",
    "KEYCLOAK_TOKEN_URL",
    "KEYCLOAK_USERINFO_URL",
    "KEYCLOAK_LOGOUT_URL",
    "KEYCLOAK_CERTS_URL",
    "oauth2_scheme",
]
