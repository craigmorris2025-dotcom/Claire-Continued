#!/usr/bin/env python3
"""
Claire v19.86.1 Source Probe Result Schema
Repair: v19.86.1.1

Fix:
- Required-field validation handles list/dict values safely.
- Empty result lists are allowed for valid "empty" probes but invalid for "success" probes.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_86_1_source_probe_result_schema"
OUT_JSON = OUT_DIR / "source_probe_result_schema.json"
CONTRACT_DIR = ROOT / "data" / "source_universes"
CONTRACT_PATH = CONTRACT_DIR / "source_probe_result_schema.json"

REQUIRED_PROBE_FIELDS = [
    "probe_id",
    "source_universe_id",
    "requested_at",
    "provider",
    "query",
    "status",
    "results",
    "source_trust_score",
    "lineage",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_missing_value(value: Any, allow_empty_list: bool = False) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list):
        return False if allow_empty_list else len(value) == 0
    if isinstance(value, (tuple, set, dict)) and len(value) == 0:
        return True
    return False


def build_schema() -> Dict[str, Any]:
    return {
        "version": "v19.86.1.1",
        "build": "Source Probe Result Schema",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "required_probe_fields": REQUIRED_PROBE_FIELDS,
        "allowed_statuses": ["success", "empty", "failed", "blocked_by_governance"],
        "result_item_fields": ["result_id", "title", "summary", "source_identifier", "source_url", "retrieved_at"],
        "lineage_fields": ["probe_id", "source_universe_id", "provider", "retrieval_path", "retrieved_at"],
    }


def validate_probe_result(probe: Dict[str, Any], schema: Dict[str, Any] | None = None) -> Dict[str, Any]:
    schema = schema or build_schema()

    missing = []
    for field in schema["required_probe_fields"]:
        if field not in probe:
            missing.append(field)
            continue
        # results may be an empty list when status == "empty"
        allow_empty_list = field == "results" and probe.get("status") in {"empty", "failed", "blocked_by_governance"}
        if is_missing_value(probe.get(field), allow_empty_list=allow_empty_list):
            missing.append(field)

    status = probe.get("status")
    if status not in schema["allowed_statuses"]:
        missing.append("valid_status")

    if status == "success" and not probe.get("results"):
        missing.append("non_empty_results_for_success")

    lineage = probe.get("lineage")
    if not isinstance(lineage, dict) or not lineage:
        missing.append("lineage_object")

    return {
        "valid": not missing,
        "status": "valid" if not missing else "invalid",
        "missing_or_invalid": missing,
    }


def write_schema() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)

    schema = build_schema()
    CONTRACT_PATH.write_text(json.dumps(schema, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.86.1.1",
        "build": "Source Probe Result Schema Repair",
        "read_only": True,
        "schema_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "schema": schema,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_schema()
    print(json.dumps({
        "status": "ok",
        "version": report["version"],
        "schema_path": report["schema_path"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
