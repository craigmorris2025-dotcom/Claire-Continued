"""
Claire Syntalion v17.88
Runtime Truth Read API Adapter

Read-only API adapter for eligible runtime truth records.
This does not enable automatic updates, autonomous execution, or runtime truth mutation.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover
    APIRouter = None

from runtime_core.governance.runtime_truth_consumption_firewall import RuntimeTruthConsumptionFirewall


def build_runtime_truth_read_payload() -> Dict[str, Any]:
    firewall = RuntimeTruthConsumptionFirewall()
    report = firewall.build_consumption_report()

    return {
        "version": "v17.88",
        "status": report.status,
        "eligible_count": report.eligible_count,
        "blocked_count": report.blocked_count,
        "runtime_truth_records": report.eligible_records,
        "blocked_records": report.blocked_records,
        "warnings": report.warnings,
        "read_only": True,
        "automatic_updates_enabled": False,
        "autonomous_agent_execution_enabled": False,
        "runtime_truth_mutation_enabled": False,
        "direct_live_probe_ingestion_enabled": False,
        "source": "runtime_truth_consumption_firewall",
    }


def get_runtime_truth_records() -> List[Dict[str, Any]]:
    payload = build_runtime_truth_read_payload()
    records = payload.get("runtime_truth_records", [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


if APIRouter is not None:
    router = APIRouter(prefix="/runtime-truth", tags=["Runtime Truth"])

    @router.get("/read")
    def read_runtime_truth() -> Dict[str, Any]:
        return build_runtime_truth_read_payload()

    @router.get("/records")
    def read_runtime_truth_records() -> Dict[str, Any]:
        records = get_runtime_truth_records()
        return {
            "version": "v17.88",
            "status": "RUNTIME_TRUTH_RECORDS_READ_ONLY",
            "count": len(records),
            "records": records,
            "read_only": True,
            "automatic_updates_enabled": False,
            "autonomous_agent_execution_enabled": False,
            "runtime_truth_mutation_enabled": False,
        }
else:
    router = None
