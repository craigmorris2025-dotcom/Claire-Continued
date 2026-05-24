from __future__ import annotations

import hashlib
import urllib.request
import urllib.error
from typing import Optional

from .models import LiveFetchRequest, LiveFetchResult
from .rate_limit_guard import RateLimitGuard
from .source_policy_bridge import LiveSourcePolicyBridge


class GovernedHttpClientAdapter:
    def __init__(
        self,
        policy: Optional[LiveSourcePolicyBridge] = None,
        rate_limit: Optional[RateLimitGuard] = None,
        live_enabled: bool = False,
    ) -> None:
        self.policy = policy or LiveSourcePolicyBridge()
        self.rate_limit = rate_limit or RateLimitGuard()
        self.live_enabled = live_enabled

    def create_request(self, url: str, purpose: str = "governed_research") -> LiveFetchRequest:
        request_id = "live_fetch_" + hashlib.sha256(f"{url}|{purpose}".encode("utf-8")).hexdigest()[:12]
        return LiveFetchRequest(request_id=request_id, url=url, purpose=purpose)

    def fetch(self, request: LiveFetchRequest) -> LiveFetchResult:
        policy = self.policy.evaluate_url(request.url)
        decision = str(policy["decision"])
        domain = str(policy["domain"])

        if decision == "blocked":
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="blocked",
                policy_decision=decision,
                error=str(policy["reason"]),
            )

        if decision == "review_required":
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="review_required",
                policy_decision=decision,
                error=str(policy["reason"]),
            )

        rate = self.rate_limit.allow(domain)
        if not rate["allowed"]:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="rate_limited",
                policy_decision=decision,
                error=str(rate["reason"]),
            )

        if not self.live_enabled:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="live_disabled_contract_ready",
                policy_decision=decision,
                text=f"LIVE_DISABLED_CONTRACT for {request.url}",
                content_type="text/plain",
            )

        try:
            http_request = urllib.request.Request(
                request.url,
                headers={
                    "User-Agent": "Claire-GovernedResearchRuntime/1.0",
                    "Accept": "text/html,text/plain,application/json;q=0.9,*/*;q=0.5",
                },
                method=request.method,
            )
            with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
                raw = response.read(request.max_bytes + 1)
                if len(raw) > request.max_bytes:
                    raw = raw[: request.max_bytes]
                text = raw.decode("utf-8", errors="replace")
                self.rate_limit.record(domain)
                return LiveFetchResult(
                    request_id=request.request_id,
                    url=request.url,
                    status="success",
                    http_status=getattr(response, "status", None),
                    content_type=response.headers.get("Content-Type"),
                    text=text,
                    policy_decision=decision,
                )
        except urllib.error.HTTPError as exc:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="http_error",
                http_status=exc.code,
                policy_decision=decision,
                error=str(exc),
            )
        except Exception as exc:
            return LiveFetchResult(
                request_id=request.request_id,
                url=request.url,
                status="fetch_error",
                policy_decision=decision,
                error=str(exc),
            )
