from __future__ import annotations

import httpx

import jwt
from jwt import PyJWKClient

from app.core.config import (
    AUTH_REDIRECT_URI,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET,
    KEYCLOAK_ISSUER,
)
from app.core.security.keycloak_auth import keycloak_token_url


class TokenExchangeError(Exception):
    """Raised when a Keycloak token request fails."""


class TokenService:
    """
    Service responsible for all communication with Keycloak's
    OpenID Connect endpoints.
    """

    def __init__(self) -> None:
        self._token_url = keycloak_token_url()

        self._logout_url = (
            f"{KEYCLOAK_ISSUER}/protocol/openid-connect/logout"
        )

        self._introspect_url = (
            f"{KEYCLOAK_ISSUER}/protocol/openid-connect/token/introspect"
        )

        self._timeout = httpx.Timeout(20.0)

        self._headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    async def _post(
        self,
        url: str,
        data: dict[str, str],
    ) -> dict:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url,
                data=data,
                headers=self._headers,
            )

        if response.status_code != 200:
            raise TokenExchangeError(
                f"Keycloak request failed "
                f"({response.status_code}): "
                f"{response.text}"
            )

        if not response.content:
            return {}

        return response.json()

    async def exchange_authorization_code(
        self,
        *,
        code: str,
        code_verifier: str,
    ) -> dict:
        return await self._post(
            self._token_url,
            {
                "grant_type": "authorization_code",
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "redirect_uri": AUTH_REDIRECT_URI,
                "code": code,
                "code_verifier": code_verifier,
            },
        )

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> dict:
        return await self._post(
            self._token_url,
            {
                "grant_type": "refresh_token",
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "refresh_token": refresh_token,
            },
        )

    async def client_credentials(self) -> dict:
        return await self._post(
            self._token_url,
            {
                "grant_type": "client_credentials",
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
            },
        )

    async def introspect_token(
        self,
        token: str,
    ) -> dict:
        return await self._post(
            self._introspect_url,
            {
                "client_id": KEYCLOAK_CLIENT_ID,
                "client_secret": KEYCLOAK_CLIENT_SECRET,
                "token": token,
            },
        )

    async def verify_id_token(self, id_token: str, access_token: str) -> dict:
        """
        Verify Keycloak ID token:
        - requires id_token + access_token to be present (signature uses id_token)
        - verifies JWT signature via JWKS
        - verifies issuer
        - verifies audience for ID token (Keycloak commonly uses aud / azp)
        - verifies exp (and nbf when present)
        """
        if not id_token or not isinstance(id_token, str):
            raise TokenExchangeError("missing_or_invalid_id_token")
        if not access_token or not isinstance(access_token, str):
            raise TokenExchangeError("missing_or_invalid_access_token")

        jwks_url = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

        try:
            unverified_header = jwt.get_unverified_header(id_token)
        except Exception as e:
            raise TokenExchangeError(f"Invalid id_token header: {e}")

        kid = unverified_header.get("kid")
        if not kid:
            raise TokenExchangeError("id_token missing 'kid' in header")

        try:
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(id_token).key
        except Exception as e:
            raise TokenExchangeError(f"Failed to fetch signing key: {e}")

        # First attempt: verify aud == client_id
        try:
            claims = jwt.decode(
                id_token,
                signing_key,
                algorithms=["RS256"],
                audience=KEYCLOAK_CLIENT_ID,
                issuer=KEYCLOAK_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                },
            )
            return claims
        except jwt.InvalidAudienceError:
            # Fallback: verify signature/issuer/exp/nbf, then manually validate aud/azp.
            try:
                claims = jwt.decode(
                    id_token,
                    signing_key,
                    algorithms=["RS256"],
                    issuer=KEYCLOAK_ISSUER,
                    options={
                        "verify_signature": True,
                        "verify_iss": True,
                        "verify_aud": False,
                        "verify_exp": True,
                        "verify_nbf": True,
                    },
                )
            except Exception as e:
                raise TokenExchangeError(f"Failed to verify id_token (fallback): {e}")

            aud = claims.get("aud")
            azp = claims.get("azp")

            aud_ok = (
                aud == KEYCLOAK_CLIENT_ID
                or (isinstance(aud, list) and KEYCLOAK_CLIENT_ID in aud)
            )
            azp_ok = azp == KEYCLOAK_CLIENT_ID

            if not (aud_ok or azp_ok):
                raise TokenExchangeError("id_token has invalid aud/azp")

            return claims
        except jwt.ExpiredSignatureError:
            raise TokenExchangeError("id_token expired")
        except jwt.ImmatureSignatureError:
            raise TokenExchangeError("id_token not yet valid (nbf)")
        except jwt.InvalidIssuerError:
            raise TokenExchangeError("id_token has invalid issuer")
        except Exception as e:
            raise TokenExchangeError(f"Failed to verify id_token: {e}")

    async def logout(
        self,
        refresh_token: str,
    ) -> None:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                self._logout_url,
                data={
                    "client_id": KEYCLOAK_CLIENT_ID,
                    "client_secret": KEYCLOAK_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                },
                headers=self._headers,
            )

        if response.status_code not in (200, 204):
            raise TokenExchangeError(
                f"Logout failed ({response.status_code}): "
                f"{response.text}"
            )
