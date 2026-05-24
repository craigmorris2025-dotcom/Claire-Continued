"""Claire Cognitive Research & Web Intelligence foundation."""

from .evidence_basket import EvidenceBasket
from .source_governance import SourceGovernance
from .web_search_adapter import WebSearchAdapter

try:
    from .research_service import ResearchService
except ImportError:
    ResearchService = None

__all__ = ["EvidenceBasket", "ResearchService", "SourceGovernance", "WebSearchAdapter"]
