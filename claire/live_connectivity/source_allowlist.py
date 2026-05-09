from __future__ import annotations
from typing import Any, Dict, List
from urllib.parse import urlparse

class SourceAllowlist:
    def build_policy(self, allowed_domains: List[str]) -> Dict[str, Any]:
        return {
            "record_type": "source_allowlist_policy",
            "allowed_domains": sorted(set(allowed_domains)),
            "default_decision": "blocked",
            "rights_required": True,
            "lineage_required": True,
        }

    def is_allowed(self, url: str, policy: Dict[str, Any]) -> bool:
        host = urlparse(url).netloc.lower()
        allowed = [d.lower() for d in policy.get("allowed_domains", [])]
        return any(host == d or host.endswith("." + d) for d in allowed)
