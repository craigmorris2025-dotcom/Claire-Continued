from __future__ import annotations
from typing import Any, Dict

class OnlineResearchPipelineContract:
    def build_contract(self) -> Dict[str, Any]:
        return {
            "record_type": "online_research_pipeline_contract",
            "stages": [
                "query_intent",
                "source_policy_check",
                "fetch_or_search",
                "lineage_record",
                "evidence_packet",
                "quarantine_or_promote",
                "operator_review",
                "benchmark_replay"
            ],
            "rule": "Online research is evidence-first and review-gated.",
        }
