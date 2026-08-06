import jwt
from jwt import PyJWKClient

from app.core.config import KEYCLOAK_ISSUER


JWKS_URL = (
    f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"
)

_jwks_client = PyJWKClient(
    JWKS_URL
)


def get_signing_key_for_token(token: str):
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(
            token
        )

        return signing_key.key

    except Exception as exc:
        raise jwt.InvalidTokenError(
            f"unable_to_get_signing_key: {exc}"
        )