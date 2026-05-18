"""Claire backend service boundary.

The active runtime still delegates to ``claire.app`` while the platform is
being cleaned and stabilized.
"""

from backend.app import create_backend_app

__all__ = ["create_backend_app"]
