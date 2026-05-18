#!/usr/bin/env python3
"""
Claire v19.85.4 Evidence Gate Runtime Adapter

Purpose:
- Provide a reusable runtime-facing adapter for evidence gate decisions.
- Combine thin-input validation and route-specific evidence threshold validation.
- Return backend-owned terminal states without mutating routes.

Read-only adapter build.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "audits" / "v19_85_4_evidence_gate_runtime_adapter"
OUT_JSON = OUT_DIR / "evidence_gate_runtime_adapter.json"
CONTRACT_DIR = ROOT / "data" / "evidence_governance"
ADAPTER_CONTRACT_PATH = CONTRACT_DIR / "evidence_gate_runtime_adapter.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_thin_input_module():
    return _load_module(ROOT / "tools" / "thin_input_escalation_blocker.py", "thin_input_escalation_blocker")


def load_threshold_module():
    return _load_module(ROOT / "tools" / "route_specific_evidence_thresholds.py", "route_specific_evidence_thresholds")


def evaluate_runtime_evidence_gate(
    raw_input: Any,
    route_type: str,
    evidence_basket: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    thin = load_thin_input_module()
    thresholds = load_threshold_module()

    route_type = (route_type or "discovery").lower()
    thin_result = thin.classify_thin_input(raw_input, route_type)

    if thin_result["allowed_to_escalate"] is False:
        return {
            "version": "v19.85.4",
            "status": thin_result["status"],
            "route_type": route_type,
            "terminal_state": thin_result["terminal_state"],
            "allowed_to_escalate": False,
            "gate": "thin_input_gate",
            "reasons": thin_result["reasons"],
            "thin_input": thin_result,
            "backend_owns_truth": True,
            "cockpit_owns_presentation_only": True,
            "operator_review_required": True,
        }

    evidence_basket = evidence_basket or {}
    route_result = thresholds.validate_route_candidate(route_type, evidence_basket)

    return {
        "version": "v19.85.4",
        "status": route_result["status"],
        "route_type": route_type,
        "terminal_state": route_result["terminal_state"],
        "allowed_to_escalate": route_result["passed"],
        "gate": "route_specific_evidence_gate",
        "reasons": route_result["reasons"],
        "thin_input": thin_result,
        "route_evidence": route_result,
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "operator_review_required": True,
    }


def build_contract() -> Dict[str, Any]:
    return {
        "version": "v19.85.4",
        "build": "Evidence Gate Runtime Adapter",
        "generated_at": utc_now(),
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "adapter_function": "evaluate_runtime_evidence_gate",
        "gate_order": ["thin_input_gate", "route_specific_evidence_gate", "operator_review_gate"],
        "valid_terminal_states": [
            "pending_evidence",
            "insufficient_data",
            "blocked_evidence",
            "review_required",
            "candidate_ready",
            "validated_candidate",
        ],
        "runtime_mutation": "none",
    }


def write_contract() -> Dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_contract()
    ADAPTER_CONTRACT_PATH.write_text(json.dumps(contract, indent=2, sort_keys=True), encoding="utf-8")
    report = {
        "version": "v19.85.4",
        "build": "Evidence Gate Runtime Adapter",
        "generated_at": utc_now(),
        "read_only": True,
        "contract_path": str(ADAPTER_CONTRACT_PATH.relative_to(ROOT)),
        "contract": contract,
        "self_checks": {
            "placeholder_breakthrough": evaluate_runtime_evidence_gate("string additionalprop1", "breakthrough"),
            "empty_discovery": evaluate_runtime_evidence_gate("", "discovery"),
        },
        "next_build": "v19.85.5 Evidence Lineage Propagation Contract",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    report = write_contract()
    print(json.dumps({
        "status": "ok",
        "version": report["version"],
        "contract_path": report["contract_path"],
        "next_build": report["next_build"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
