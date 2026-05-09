from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .content_normalizer import ContentNormalizer
from .evidence_persistence import EvidencePersistence
from .http_client_adapter import GovernedHttpClientAdapter
from .retry_deadletter import RetryDeadLetterManager
from .source_policy_bridge import LiveSourcePolicyBridge


class LiveIngestionWorker:
    def __init__(
        self,
        live_enabled: bool = False,
        evidence_root: Path | None = None,
    ) -> None:
        self.policy = LiveSourcePolicyBridge()
        self.http = GovernedHttpClientAdapter(policy=self.policy, live_enabled=live_enabled)
        self.normalizer = ContentNormalizer()
        self.persistence = EvidencePersistence(evidence_root)
        self.retry = RetryDeadLetterManager()

    def ingest_url(self, url: str, purpose: str = "governed_research") -> Dict[str, Any]:
        request = self.http.create_request(url=url, purpose=purpose)
        result = self.http.fetch(request)

        output: Dict[str, Any] = {
            "request": request.to_dict(),
            "fetch_result": result.to_dict(),
            "normalized": None,
            "evidence_record": None,
            "saved_path": None,
            "retry_state": self.retry.snapshot(),
        }

        if result.status not in {"success", "live_disabled_contract_ready"}:
            if self.retry.should_retry(result.request_id, result.status):
                output["retry_state"] = self.retry.record_failure(result.request_id, result.status, result.error)
            return output

        normalized = self.normalizer.normalize(result)
        reliability = 0.5 if result.status == "live_disabled_contract_ready" else 0.7
        record = self.persistence.create_record(normalized, reliability_score=reliability)
        saved = self.persistence.save(record)

        output["normalized"] = normalized.to_dict()
        output["evidence_record"] = record.to_dict()
        output["saved_path"] = str(saved)
        return output
