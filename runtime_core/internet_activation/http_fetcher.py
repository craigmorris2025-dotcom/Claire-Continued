from __future__ import annotations

import asyncio
from typing import Optional

import aiohttp

from .config import InternetActivationConfig
from .models import FetchResult
from .policy import InternetPolicyEngine


class GovernedHttpFetcher:
    def __init__(self, config: InternetActivationConfig, policy: Optional[InternetPolicyEngine] = None) -> None:
        self.config = config
        self.policy = policy or InternetPolicyEngine(config)

    async def fetch(self, url: str) -> FetchResult:
        policy_decision = self.policy.evaluate_url(url)
        if policy_decision.decision in {"blocked", "review_required"}:
            return FetchResult(url=url, status=policy_decision.decision, error=policy_decision.reason, policy=policy_decision.to_dict())

        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        headers = {
            "User-Agent": "Claire-InternetActivation/17.41 (+governed research)",
            "Accept": "text/html,text/plain,application/json,application/pdf,application/xml,text/xml;q=0.9,*/*;q=0.2",
        }
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    content_type = response.headers.get("Content-Type")
                    content_policy = self.policy.evaluate_content_type(content_type)
                    if not content_policy.content_allowed:
                        return FetchResult(url=str(response.url), status="blocked_content_type", http_status=response.status, content_type=content_type, error=content_policy.reason, policy={"url_policy": policy_decision.to_dict(), "content_policy": content_policy.to_dict()})
                    raw = await response.content.read(self.config.max_bytes + 1)
                    truncated = len(raw) > self.config.max_bytes
                    raw = raw[: self.config.max_bytes]
                    return FetchResult(
                        url=str(response.url),
                        status="success" if response.status < 400 else "http_error",
                        http_status=response.status,
                        content_type=content_type,
                        text=self._decode(raw, content_type),
                        binary_size=len(raw),
                        error="Content truncated at max_bytes." if truncated else None,
                        policy={"url_policy": policy_decision.to_dict(), "content_policy": content_policy.to_dict(), "truncated": truncated},
                    )
        except asyncio.TimeoutError:
            return FetchResult(url=url, status="timeout", error=f"Fetch timed out after {self.config.timeout_seconds} seconds.", policy=policy_decision.to_dict())
        except Exception as exc:
            return FetchResult(url=url, status="fetch_error", error=str(exc), policy=policy_decision.to_dict())

    def _decode(self, raw: bytes, content_type: Optional[str]) -> str:
        if not raw:
            return ""
        if content_type and "application/pdf" in content_type.lower():
            return f"[PDF downloaded safely: {len(raw)} bytes. Text extraction requires optional PDF parser.]"
        return raw.decode("utf-8", errors="replace")
