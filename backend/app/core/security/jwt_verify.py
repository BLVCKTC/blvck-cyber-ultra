import jwt

from app.core.config import KEYCLOAK_ISSUER, KEYCLOAK_ALLOWED_AUDIENCE
from app.core.security.jwks import get_signing_key_for_token


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return value
    return []


def verify_keycloak_access_token(access_token: str) -> dict:
    print("PyJWT version:", jwt.__version__)
    signing_key = get_signing_key_for_token(access_token)

    expected_aud = (KEYCLOAK_ALLOWED_AUDIENCE or "").strip()

    try:
        unverified_claims = jwt.decode(
            access_token,
            options={"verify_signature": False, "verify_aud": False},
        )
        print("UNVERIFIED decode ok")
    except Exception as e:
        print("UNVERIFIED decode FAILED:", repr(e))
        raise

    token_aud = unverified_claims.get("aud")
    aud_list = _as_list(token_aud)

    if token_aud is not None and expected_aud:
        if expected_aud not in aud_list:
            raise jwt.InvalidTokenError("invalid_aud")

    try:
        claims = jwt.decode(
            access_token,
            signing_key,
            algorithms=["RS256"],
            issuer=KEYCLOAK_ISSUER,
            options={"verify_aud": False},
        )
        print("FULL decode ok")
    except Exception as e:
        print("FULL decode FAILED:", repr(e))
        raise

    return claims
