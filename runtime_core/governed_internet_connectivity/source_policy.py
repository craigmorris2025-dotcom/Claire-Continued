from __future__ import annotations

from urllib.parse import urlparse
from typing import Dict, Optional

from .models import SourcePolicy


class SourcePolicyEngine:
    def __init__(self, policy: Optional[SourcePolicy] = None) -> None:
        self.policy = policy or SourcePolicy(
            allowed_domains=[
                "sec.gov",
                "federalregister.gov",
                "congress.gov",
                "nist.gov",
                "nih.gov",
                "who.int",
                "oecd.org",
                "worldbank.org",
                "imf.org",
                "reuters.com",
                "apnews.com",
            ],
            blocked_domains=[],
            require_review_for_unknown_sources=True,
            max_fetches_per_run=10,
            governance_mode="review_first",
        )

    def domain_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace("www.", "")

    def evaluate(self, source_url: Optional[str], domain: Optional[str] = None) -> Dict[str, object]:
        resolved_domain = domain or (self.domain_from_url(source_url) if source_url else None)

        if not resolved_domain:
            return {
                "decision": "search_only",
                "domain": None,
                "requires_review": True,
                "reason": "No domain supplied; search request must remain bounded.",
            }

        if resolved_domain in self.policy.blocked_domains:
            return {
                "decision": "blocked",
                "domain": resolved_domain,
                "requires_review": True,
                "reason": "Domain is explicitly blocked.",
            }

        if resolved_domain in self.policy.allowed_domains:
            return {
                "decision": "allowed",
                "domain": resolved_domain,
                "requires_review": False,
                "reason": "Domain is on governed allowlist.",
            }

        return {
            "decision": "review_required",
            "domain": resolved_domain,
            "requires_review": self.policy.require_review_for_unknown_sources,
            "reason": "Domain is unknown and requires operator review.",
        }
