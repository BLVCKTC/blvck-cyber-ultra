# app/services/pkce_service.py

from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.security.keycloak_auth import keycloak_authorize_url
from app.db.models.pkce_attempt import PKCEAttempt


class PKCEService:
    """
    Handles OAuth2/OIDC Authorization Code + PKCE login attempts.
    """

    EXPIRY_MINUTES = 10

    def __init__(self, db: Session):
        self.db = db

    def _generate_code_challenge(self, verifier: str) -> str:
        """S256(code_verifier) per RFC 7636."""
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    def create_login_request(self, tenant_id: uuid.UUID | None = None) -> dict[str, str]:

        attempt_id = uuid.uuid4()
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = self._generate_code_challenge(code_verifier)

        attempt = PKCEAttempt(
            attempt_id=attempt_id,
            tenant_id=tenant_id,
            code_verifier=code_verifier,
        )

        self.db.add(attempt)
        self.db.commit()

        return {
            "attempt_id": str(attempt_id),
            "authorization_url": keycloak_authorize_url(
                state=str(attempt_id),
                code_challenge=code_challenge,
            ),
        }

    def consume_attempt(self, attempt_id: str) -> dict[str, str | uuid.UUID | None]:
        try:
            attempt_uuid = uuid.UUID(attempt_id)
        except (ValueError, TypeError, AttributeError):
            raise HTTPException(status_code=400, detail="invalid_pkce_attempt")

        attempt = (
            self.db.query(PKCEAttempt)
            .filter(PKCEAttempt.attempt_id == attempt_uuid)
            .first()
        )

        if not attempt:
            raise HTTPException(status_code=400, detail="invalid_pkce_attempt")

        # Extract data before deletion
        tenant_id = attempt.tenant_id
        code_verifier = attempt.code_verifier
        created_at = attempt.created_at

        # Always delete the attempt immediately to prevent replay attacks
        self.db.delete(attempt)
        self.db.commit()

        # Use naive UTC comparison for naive DB columns
        if created_at < datetime.utcnow() - timedelta(minutes=self.EXPIRY_MINUTES):
            raise HTTPException(status_code=400, detail="expired_pkce_attempt")

        return {
            "tenant_id": tenant_id,
            "code_verifier": code_verifier,
        }

    def cleanup_expired_attempts(self) -> int:
        cutoff = datetime.utcnow() - timedelta(minutes=self.EXPIRY_MINUTES)
        result = self.db.execute(
            delete(PKCEAttempt).where(PKCEAttempt.created_at < cutoff)
        )
        self.db.commit()
        return result.rowcount or 0
