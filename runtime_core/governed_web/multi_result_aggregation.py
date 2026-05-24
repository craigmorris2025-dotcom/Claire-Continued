from datetime import datetime
from typing import Any, Dict, List


class GovernedMultiResultAggregator:
    def __init__(self) -> None:
        self.aggregator_version = "v18.43"
        self.fail_closed = True

    def aggregate(
        self,
        provider_results: List[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:

        merged_results: List[Dict[str, Any]] = []
        seen_keys = set()

        for provider_batch in provider_results:
            for result in provider_batch:

                url = str(result.get("url", "")).strip()
                title = str(result.get("title", "")).strip()

                dedupe_key = f"{title}|{url}"

                if dedupe_key in seen_keys:
                    continue

                seen_keys.add(dedupe_key)

                merged_results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": str(
                            result.get("snippet", "")
                        ),
                        "source_trust_level": str(
                            result.get(
                                "source_trust_level",
                                "unverified",
                            )
                        ),
                        "provider": str(
                            result.get(
                                "provider",
                                "unknown",
                            )
                        ),
                    }
                )

        return {
            "aggregator_version": self.aggregator_version,
            "created_utc": datetime.utcnow().isoformat() + "Z",
            "result_count": len(merged_results),
            "results": merged_results,
            "governance_state": self.governance_state(),
        }

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_gate_enforced": True,
            "multi_result_aggregation_enabled": True,
            "dedupe_enabled": True,
            "fail_closed_mode": True,
        }
