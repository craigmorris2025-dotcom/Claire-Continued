from __future__ import annotations

from typing import Any, Dict

from .models import RetryPolicy


class FailureClassifier:
    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        self.retry_policy = retry_policy or RetryPolicy()

    def classify(self, status: str, message: str = "") -> Dict[str, object]:
        normalized = (status or "unknown").lower()
        text = (message or "").lower()

        if normalized in {"timeout"} or "timed out" in text or "timeout" in text:
            category = "timeout"
            retryable = True
        elif normalized in {"blocked", "review_required"}:
            category = "governance_block"
            retryable = False
        elif normalized in {"not_configured"}:
            category = "configuration"
            retryable = False
        elif normalized in {"http_error"}:
            category = "remote_http_error"
            retryable = True
        elif normalized in {"fetch_error", "failed", "completed_with_failures"}:
            category = "runtime_failure"
            retryable = True
        elif normalized in {"completed_no_evidence"}:
            category = "no_evidence"
            retryable = False
        else:
            category = "unknown"
            retryable = normalized in self.retry_policy.retry_statuses

        if normalized in self.retry_policy.non_retry_statuses:
            retryable = False

        return {
            "category": category,
            "retryable": retryable,
            "status": normalized,
        }
