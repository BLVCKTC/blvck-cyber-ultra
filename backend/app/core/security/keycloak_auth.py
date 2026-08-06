from urllib.parse import urlencode

from app.core.config import (
    KEYCLOAK_URL,
    KEYCLOAK_REALM,
    KEYCLOAK_CLIENT_ID,
    AUTH_REDIRECT_URI,
)


def keycloak_authorize_url(
    state: str,
    redirect_uri: str = AUTH_REDIRECT_URI,
    code_challenge: str | None = None,
) -> str:
    base = (
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
        "/protocol/openid-connect/auth"
    )

    params = {
        "client_id": KEYCLOAK_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    }

    # PKCE support
    if code_challenge:
        params.update(
            {
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
            }
        )

    return f"{base}?{urlencode(params)}"


def keycloak_token_url() -> str:
    return (
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
        "/protocol/openid-connect/token"
    )