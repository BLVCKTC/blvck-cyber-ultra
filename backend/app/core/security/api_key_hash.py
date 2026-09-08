from __future__ import annotations

import hashlib
import secrets

KEY_BYTES = 32  # 256 bits of entropy
PREFIX_LENGTH = 8


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new raw API key.

    Returns (raw_key, key_prefix, key_hash):
    - raw_key: the full secret, shown to the user exactly once
    - key_prefix: a short, non-secret identifier shown in lists/logs
      so a key can be recognized without exposing the secret
    - key_hash: SHA-256 hex digest, the only form ever persisted
    """
    raw_key = f"blvk_{secrets.token_urlsafe(KEY_BYTES)}"
    key_prefix = raw_key[:PREFIX_LENGTH]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return raw_key, key_prefix, key_hash


def hash_api_key(raw_key: str) -> str:
    """Hash a presented raw key the same way, for future verification
    once the auth middleware exists."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()