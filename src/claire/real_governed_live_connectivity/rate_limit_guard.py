from __future__ import annotations

from collections import defaultdict
from typing import Dict


class RateLimitGuard:
    def __init__(self, max_per_domain_per_run: int = 3, max_total_per_run: int = 10) -> None:
        self.max_per_domain_per_run = max_per_domain_per_run
        self.max_total_per_run = max_total_per_run
        self.domain_counts: Dict[str, int] = defaultdict(int)
        self.total_count = 0

    def allow(self, domain: str) -> dict:
        if self.total_count >= self.max_total_per_run:
            return {"allowed": False, "reason": "Total run fetch limit reached."}
        if self.domain_counts[domain] >= self.max_per_domain_per_run:
            return {"allowed": False, "reason": "Domain fetch limit reached."}
        return {"allowed": True, "reason": "Rate limit allows request."}

    def record(self, domain: str) -> None:
        self.domain_counts[domain] += 1
        self.total_count += 1

    def snapshot(self) -> dict:
        return {
            "max_per_domain_per_run": self.max_per_domain_per_run,
            "max_total_per_run": self.max_total_per_run,
            "domain_counts": dict(self.domain_counts),
            "total_count": self.total_count,
        }
