"""
Claire v17.62 Dashboard Intelligence Foundation.

This package creates a local search/intelligence index for dashboard-facing
truth files. It is intentionally local and honest: no fake internet search,
no fake standalone intelligence, and no memory mutation.
"""

from .local_index import build_dashboard_intelligence_index

__all__ = ["build_dashboard_intelligence_index"]
