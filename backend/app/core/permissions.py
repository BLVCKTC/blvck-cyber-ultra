from __future__ import annotations

"""
LEGACY COMPATIBILITY LAYER.

This module exists to prevent breaking imports during the migration to app.api.deps.
All new routes MUST import require_permission directly from app.api.deps.

Example:
    from app.api.deps import require_permission
"""

from app.api.deps import require_permission

__all__ = ["require_permission"]
