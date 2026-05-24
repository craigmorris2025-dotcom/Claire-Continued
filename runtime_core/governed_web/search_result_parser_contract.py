from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


MAX_SNIPPET_LENGTH = 512


@dataclass
class ParsedSearchResult:
    title: str
    url: str
    snippet: str
    source_trust_level: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source_trust_level": self.source_trust_level,
            "metadata": self.metadata,
        }


@dataclass
class SearchParserContractResult:
    parser_version: str
    created_utc: str
    result_count: int
    results: List[Dict[str, Any]]
    governance_state: Dict[str, Any]


class GovernedSearchResultParser:
    def __init__(self) -> None:
        self.parser_version = "v18.37"
        self.fail_closed = True

    def parse(self, records: List[Dict[str, Any]]) -> SearchParserContractResult:
        parsed_results = []

        for record in records:
            snippet = str(record.get("snippet", ""))[:MAX_SNIPPET_LENGTH]

            parsed = ParsedSearchResult(
                title=str(record.get("title", "")),
                url=str(record.get("url", "")),
                snippet=snippet,
                source_trust_level=str(
                    record.get("source_trust_level", "unverified")
                ),
                metadata={
                    "body_truncated": len(
                        str(record.get("snippet", ""))
                    ) > MAX_SNIPPET_LENGTH,
                    "metadata_only": bool(
                        record.get("metadata_only", False)
                    ),
                },
            )

            parsed_results.append(parsed.to_dict())

        return SearchParserContractResult(
            parser_version=self.parser_version,
            created_utc=datetime.utcnow().isoformat() + "Z",
            result_count=len(parsed_results),
            results=parsed_results,
            governance_state=self.governance_state(),
        )

    def governance_state(self) -> Dict[str, Any]:
        return {
            "runtime_truth_mutation": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
            "review_required": True,
            "fail_closed_mode": True,
            "parser_contract_enforced": True,
        }
