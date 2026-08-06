import base64
import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.security.keycloak_auth import keycloak_authorize_url
from app.db.models.pkce_attempt import PKCEAttempt


class PKCEService:
    """
    Handles the complete PKCE lifecycle.

    Responsibilities:
    - Generate PKCE verifier/challenge
    - Store temporary login attempts
    - Build Keycloak authorization URL
    - Consume attempts exactly once
    - Cleanup expired attempts
    """

    EXPIRY_MINUTES = 10

    def __init__(self, db: Session):
        self.db = db

    def _now(self) -> datetime:
        """
        created_at is stored as UTC naive datetime.
        """
        return datetime.utcnow()

    def _generate_attempt_id(self) -> str:
        return secrets.token_urlsafe(32)

    def _generate_code_verifier(self) -> str:
        """
        RFC7636 code verifier.
        """
        return secrets.token_urlsafe(64)

    def _generate_code_challenge(self, verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()

        return (
            base64.urlsafe_b64encode(digest)
            .decode("ascii")
            .rstrip("=")
        )

    def create_login_request(
        self,
        tenant_id: str,
    ) -> dict[str, str]:
        """
        Creates a PKCE login attempt.

        Returns:
        {
            "attempt_id": "...",
            "authorization_url": "https://keycloak/..."
        }
        """

        attempt_id = self._generate_attempt_id()

        code_verifier = self._generate_code_verifier()

        code_challenge = self._generate_code_challenge(
            code_verifier
        )

        attempt = PKCEAttempt(
            attempt_id=attempt_id,
            tenant_id=tenant_id,
            code_verifier=code_verifier,
        )

        self.db.add(attempt)
        self.db.commit()

        authorization_url = keycloak_authorize_url(
            state=attempt_id,
            code_challenge=code_challenge,
        )

        return {
            "attempt_id": attempt_id,
            "authorization_url": authorization_url,
        }

    def consume_attempt(
        self,
        attempt_id: str,
    ) -> dict[str, str]:
        """
        Consumes a PKCE attempt exactly once.

        Returns:
        {
            "tenant_id": "...",
            "code_verifier": "..."
        }
        """

        attempt = (
            self.db.query(PKCEAttempt)
            .filter(
                PKCEAttempt.attempt_id == attempt_id
            )
            .first()
        )

        if attempt is None:
            raise HTTPException(
                status_code=400,
                detail="invalid_pkce_attempt",
            )

        expired = (
            attempt.created_at
            < self._now()
            - timedelta(minutes=self.EXPIRY_MINUTES)
        )

        # Delete immediately to prevent replay
        self.db.delete(attempt)
        self.db.commit()

        if expired:
            raise HTTPException(
                status_code=400,
                detail="expired_pkce_attempt",
            )

        return {
            "tenant_id": attempt.tenant_id,
            "code_verifier": attempt.code_verifier,
        }

    def cleanup_expired_attempts(self) -> int:
        """
        Deletes expired PKCE attempts.

        Returns:
            Number of deleted rows.
        """

        cutoff = (
            self._now()
            - timedelta(minutes=self.EXPIRY_MINUTES)
        )

        result = self.db.execute(
            delete(PKCEAttempt).where(
                PKCEAttempt.created_at < cutoff
            )
        )

        self.db.commit()

        return result.rowcount or 0