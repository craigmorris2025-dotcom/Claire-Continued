from datetime import datetime
from typing import Any, Dict, List


TRUST_SCORES = {
    "high": 0.90,
    "medium": 0.65,
    "low": 0.35,
    "unverified": 0.10,
}


class SearchTrustScoringNormalization:
    def __init__(self) -> None:
        self.normalization_version = "v18.44"
        self.fail_closed = True

    def normalize(
        self,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        normalized_results = []

        for result in results:
            trust_level = str(
                result.get(
                    "source_trust_level",
                    "unverified",
                )
            ).lower()

            trust_score = TRUST_SCORES.get(
                trust_level,
                TRUST_SCORES["unverified"],
            )

            normalized_results.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "source_trust_level": trust_level,
                    "trust_score": trust_score,
                    "provider": result.get("provider", "unknown"),
                }
            )

        return {
            "normalization_version": self.normalization_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "result_count": len(normalized_results),
            "results": normalized_results,
            "governance_state": self.governance_state(),
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "trust_normalization_enabled": True,
            "review_gate_enforced": True,
            "fail_closed_mode": True,
        }
