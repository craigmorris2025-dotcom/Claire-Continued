from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .config import InternetActivationConfig
from .models import PolicyDecision


class InternetPolicyEngine:
    def __init__(self, config: InternetActivationConfig) -> None:
        self.config = config

    def domain_from_url(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")

    def extension_from_url(self, url: str) -> str:
        return Path(urlparse(url).path).suffix.lower()

    def evaluate_url(self, url: str) -> PolicyDecision:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return PolicyDecision("blocked", url=url, reason="Only http and https URLs are allowed.", requires_review=True, content_allowed=False)
        domain = self.domain_from_url(url)
        if not domain:
            return PolicyDecision("blocked", url=url, reason="URL has no valid domain.", requires_review=True, content_allowed=False)
        ext = self.extension_from_url(url)
        if ext in self.config.blocked_extensions:
            return PolicyDecision("blocked", url=url, domain=domain, reason=f"Blocked file extension: {ext}", requires_review=True, content_allowed=False)
        if domain in set(self.config.blocked_domains):
            return PolicyDecision("blocked", url=url, domain=domain, reason="Domain is explicitly blocked.", requires_review=True, content_allowed=False)
        allowed = set(self.config.allowed_domains)
        if domain in allowed or any(domain.endswith("." + item) for item in allowed):
            return PolicyDecision("allowed", url=url, domain=domain, reason="Domain is allowlisted.")
        if self.config.allow_unknown_domains:
            return PolicyDecision("allowed_unknown", url=url, domain=domain, reason="Unknown domain allowed by config.")
        return PolicyDecision("review_required", url=url, domain=domain, reason="Unknown domain requires review before fetch.", requires_review=True, content_allowed=False)

    def evaluate_content_type(self, content_type: Optional[str]) -> PolicyDecision:
        if not content_type:
            return PolicyDecision("allowed", reason="No content type provided; enforcing byte and text limits.")
        base = content_type.split(";")[0].strip().lower()
        if base in set(self.config.allowed_content_types):
            return PolicyDecision("allowed", reason=f"Allowed content type: {base}")
        return PolicyDecision("blocked", reason=f"Blocked content type: {base}", requires_review=True, content_allowed=False)
