"""
Claire Syntalion v17.87.1
Runtime Truth Consumption Firewall Repair

Fix:
- Adds the missing datetime/timezone import required by _utc_now().
- Preserves v17.87 behavior and tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json


@dataclass
class RuntimeTruthConsumptionReport:
    status: str
    eligible_count: int
    blocked_count: int
    eligible_records: List[Dict[str, Any]]
    blocked_records: List[Dict[str, Any]]
    warnings: List[str]


class RuntimeTruthConsumptionFirewall:
    def __init__(
        self,
        ledger_path: str | Path = "data/runtime_truth/runtime_truth_ledger.json",
        report_path: str | Path = "data/runtime_truth/runtime_truth_consumption_report.json",
    ) -> None:
        self.ledger_path = Path(ledger_path)
        self.report_path = Path(report_path)

    def _read_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def _write_json(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _records(self, ledger: Any) -> List[Dict[str, Any]]:
        if not isinstance(ledger, dict):
            return []
        records = ledger.get("records", [])
        if not isinstance(records, list):
            return []
        return [record for record in records if isinstance(record, dict)]

    def evaluate_record(self, record: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []

        if not record.get("runtime_truth_id"):
            reasons.append("missing_runtime_truth_id")

        if not record.get("evidence_id"):
            reasons.append("missing_evidence_id")

        if record.get("ingestion_mode") != "manual_reviewed_append_only":
            reasons.append("invalid_ingestion_mode")

        if not record.get("source_provenance"):
            reasons.append("missing_source_provenance")

        if not record.get("approved_by"):
            reasons.append("missing_approved_by")

        if not record.get("approved_at"):
            reasons.append("missing_approved_at")

        lineage = record.get("lineage")
        if not isinstance(lineage, dict):
            reasons.append("missing_lineage")
            return reasons

        if lineage.get("live_probe_direct_ingestion") is not False:
            reasons.append("live_probe_direct_ingestion_not_false")

        if lineage.get("automatic_update") is not False:
            reasons.append("automatic_update_not_false")

        if lineage.get("autonomous_ingestion") is not False:
            reasons.append("autonomous_ingestion_not_false")

        if lineage.get("candidate_review_status") != "approved":
            reasons.append("candidate_review_status_not_approved")

        if lineage.get("candidate_promotion_status") != "approved_for_runtime_truth":
            reasons.append("candidate_promotion_status_not_approved_for_runtime_truth")

        return reasons

    def build_consumption_report(self) -> RuntimeTruthConsumptionReport:
        ledger = self._read_json(self.ledger_path, {"records": []})
        records = self._records(ledger)

        eligible: List[Dict[str, Any]] = []
        blocked: List[Dict[str, Any]] = []
        warnings: List[str] = []

        if not records:
            warnings.append("runtime_truth_ledger_empty")

        seen_evidence_ids = set()

        for record in records:
            evidence_id = record.get("evidence_id")
            reasons = self.evaluate_record(record)

            if evidence_id in seen_evidence_ids:
                reasons.append("duplicate_evidence_id_in_ledger")

            if evidence_id:
                seen_evidence_ids.add(evidence_id)

            if reasons:
                blocked.append(
                    {
                        "runtime_truth_id": record.get("runtime_truth_id", "UNKNOWN"),
                        "evidence_id": evidence_id or "UNKNOWN",
                        "blocked_reasons": reasons,
                    }
                )
                continue

            eligible.append(
                {
                    "runtime_truth_id": record.get("runtime_truth_id"),
                    "evidence_id": evidence_id,
                    "source_provenance": record.get("source_provenance"),
                    "truth_payload": record.get("truth_payload"),
                    "consumption_status": "eligible_for_governed_runtime_read",
                    "read_only": True,
                }
            )

        status = "NO_RUNTIME_TRUTH_AVAILABLE"
        if eligible and blocked:
            status = "PARTIAL_RUNTIME_TRUTH_CONSUMPTION_READY_WITH_BLOCKS"
        elif eligible:
            status = "RUNTIME_TRUTH_CONSUMPTION_READY"
        elif blocked:
            status = "ALL_RUNTIME_TRUTH_RECORDS_BLOCKED"

        payload = {
            "version": "v17.87.1",
            "generated_at": self._utc_now(),
            "status": status,
            "eligible_count": len(eligible),
            "blocked_count": len(blocked),
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
            "eligible_records": eligible,
            "blocked_records": blocked,
            "warnings": warnings,
        }

        self._write_json(self.report_path, payload)

        return RuntimeTruthConsumptionReport(
            status=status,
            eligible_count=len(eligible),
            blocked_count=len(blocked),
            eligible_records=eligible,
            blocked_records=blocked,
            warnings=warnings,
        )

    def get_eligible_runtime_truth(self) -> List[Dict[str, Any]]:
        report = self.build_consumption_report()
        return report.eligible_records
