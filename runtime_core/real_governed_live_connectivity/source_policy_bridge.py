from __future__ import annotations

from typing import Dict
from urllib.parse import urlparse


class LiveSourcePolicyBridge:
    DEFAULT_ALLOWED = {
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
    }

    def __init__(self, allowed_domains: set[str] | None = None, blocked_domains: set[str] | None = None) -> None:
        self.allowed_domains = allowed_domains or set(self.DEFAULT_ALLOWED)
        self.blocked_domains = blocked_domains or set()

    def domain_from_url(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")

    def evaluate_url(self, url: str) -> Dict[str, object]:
        domain = self.domain_from_url(url)
        if domain in self.blocked_domains:
            return {
                "decision": "blocked",
                "domain": domain,
                "requires_review": True,
                "reason": "Domain is explicitly blocked.",
            }
        if domain in self.allowed_domains:
            return {
                "decision": "allowed",
                "domain": domain,
                "requires_review": False,
                "reason": "Domain is allowed for governed fetch.",
            }
        return {
            "decision": "review_required",
            "domain": domain,
            "requires_review": True,
            "reason": "Unknown domain requires review before live fetch.",
        }
