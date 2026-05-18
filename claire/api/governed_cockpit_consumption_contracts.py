
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping


LOCKED_AUTHORITY = {
    "runtime_truth_mutation": False,
    "automatic_updates": False,
    "autonomous_execution": False,
    "continuous_live_crawling": False,
    "browser_execution": False,
    "javascript_execution": False,
}


PANEL_ORDER = [
    "system_inventory",
    "web_needs",
    "research_queue",
    "source_policy",
    "approved_fetch_plans",
    "quarantined_evidence",
    "extraction_reports",
    "manual_promotion_status",
    "update_proposal_status",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"available": False, "path": str(path), "reason": "missing"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("available", True)
            data.setdefault("path", str(path))
            return data
        return {"available": True, "path": str(path), "value": data}
    except Exception as exc:
        return {"available": False, "path": str(path), "reason": f"unreadable:{type(exc).__name__}"}


def normalize_panel_contract(name: str, source: Mapping[str, Any]) -> Dict[str, Any]:
    available = bool(source.get("available", False))
    panel = {
        "panel": name,
        "available": available,
        "path": source.get("path"),
        "status": "available" if available else "unavailable",
        "summary": {
            "record_type": source.get("record_type"),
            "version": source.get("version"),
            "candidate_count": source.get("candidate_count"),
            "blocked_count": source.get("blocked_count"),
            "ready_count": source.get("ready_count"),
            "missing_count": source.get("missing_count"),
            "available_count": source.get("available_count"),
            "reason": source.get("reason"),
        },
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "promotion_effect": "none",
    }
    panel["panel_sha256"] = _sha256(panel)
    return panel


def build_cockpit_panel_contracts(root: Path) -> Dict[str, Any]:
    output = root / "output"
    truth_payload = _read_json(output / "backend_truth_surfaces" / "backend_truth_surface_payload.json")
    truth_status = _read_json(output / "backend_truth_surfaces" / "backend_truth_surface_status.json")

    surfaces = dict(truth_status.get("surfaces", {}) or {})
    manual = dict(truth_payload.get("manual_promotion", {}) or {})

    raw_sources = {
        "system_inventory": surfaces.get("system_inventory", {"available": False, "reason": "missing"}),
        "web_needs": surfaces.get("web_needs", {"available": False, "reason": "missing"}),
        "research_queue": surfaces.get("research_queue", {"available": False, "reason": "missing"}),
        "source_policy": surfaces.get("source_policy", {"available": False, "reason": "missing"}),
        "approved_fetch_plans": surfaces.get("approved_fetch_plans", {"available": False, "reason": "missing"}),
        "quarantined_evidence": surfaces.get("quarantined_evidence", {"available": False, "reason": "missing"}),
        "extraction_reports": surfaces.get("extraction_reports", {"available": False, "reason": "missing"}),
        "manual_promotion_status": manual.get("plateau_report", surfaces.get("manual_promotion_status", {"available": False, "reason": "missing"})),
        "update_proposal_status": manual.get("package_index", surfaces.get("update_proposal_status", {"available": False, "reason": "missing"})),
    }

    panels = [normalize_panel_contract(name, raw_sources.get(name, {})) for name in PANEL_ORDER]
    payload = {
        "record_type": "cockpit_consumption_contracts",
        "version": "v19.89.8-S40R5-R8",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "panel_order": list(PANEL_ORDER),
        "panel_count": len(panels),
        "available_panel_count": sum(1 for panel in panels if panel.get("available") is True),
        "panels": panels,
        "source_truth_payload_available": truth_payload.get("available", False),
        "source_truth_status_available": truth_status.get("available", False),
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "browser_execution_allowed": False,
        "javascript_execution_allowed": False,
        "created_at": _utc_now(),
    }
    payload["contracts_sha256"] = _sha256(payload)
    return payload


def build_cockpit_panel_index(contracts: Mapping[str, Any]) -> Dict[str, Any]:
    panels = list(contracts.get("panels", []) or [])
    index = {
        "record_type": "cockpit_panel_index",
        "version": "v19.89.8-S40R5-R8",
        "panel_count": len(panels),
        "panels": [
            {
                "panel": panel.get("panel"),
                "available": panel.get("available"),
                "status": panel.get("status"),
                "panel_sha256": panel.get("panel_sha256"),
            }
            for panel in panels
        ],
        "authority": dict(LOCKED_AUTHORITY),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    index["panel_index_sha256"] = _sha256(index)
    return index


def verify_cockpit_contracts(contracts: Mapping[str, Any]) -> Dict[str, Any]:
    panels = list(contracts.get("panels", []) or [])
    failures: List[str] = []
    if contracts.get("runtime_truth_mutation_allowed") is not False:
        failures.append("contracts_runtime_truth_mutation_not_false")
    if contracts.get("automatic_update_allowed") is not False:
        failures.append("contracts_automatic_update_not_false")
    if contracts.get("cockpit_presentation_only") is not True:
        failures.append("cockpit_presentation_only_missing")
    if [panel.get("panel") for panel in panels] != PANEL_ORDER:
        failures.append("panel_order_mismatch")
    for panel in panels:
        if panel.get("runtime_truth_mutation_allowed") is not False:
            failures.append(f"{panel.get('panel')}_runtime_mutation_not_false")
        if panel.get("automatic_update_allowed") is not False:
            failures.append(f"{panel.get('panel')}_automatic_update_not_false")

    report = {
        "record_type": "cockpit_consumption_contract_verification",
        "version": "v19.89.8-S40R5-R8",
        "verification_ok": not failures,
        "failures": failures,
        "panel_count": len(panels),
        "runtime_truth_mutation_allowed": False,
        "automatic_update_allowed": False,
        "created_at": _utc_now(),
    }
    report["verification_sha256"] = _sha256(report)
    return report


def write_cockpit_consumption_contracts(root: Path, output_dir: Path) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    contracts = build_cockpit_panel_contracts(root)
    index = build_cockpit_panel_index(contracts)
    verification = verify_cockpit_contracts(contracts)

    files = {
        "contracts": output_dir / "cockpit_consumption_contracts.json",
        "panel_index": output_dir / "cockpit_panel_index.json",
        "verification": output_dir / "cockpit_consumption_contract_verification.json",
    }
    files["contracts"].write_text(json.dumps(contracts, indent=2, sort_keys=True), encoding="utf-8")
    files["panel_index"].write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    files["verification"].write_text(json.dumps(verification, indent=2, sort_keys=True), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}
