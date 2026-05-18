
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

VERSION = "v17.75.1"
CONTRACT_NAME = "Dashboard Backend Bridge Repair"

STATE_PATH = Path("data/dashboard/operator_dashboard_state.json")

INPUTS = {
    "proof_pack": Path("data/proof/full_end_to_end_proof_pack.json"),
    "stop_go": Path("data/proof/v17_75_stop_go_report.json"),
    "runtime_truth": Path("data/runtime/runtime_truth_canonical.json"),
    "dashboard_runtime_truth": Path("data/runtime/dashboard_runtime_truth.json"),
    "route_audit": Path("data/routes/discovery_breakthrough_innovation_route_audit.json"),
    "autodesign_handoff": Path("data/autodesign/autodesign_handoff_contract.json"),
    "design_portal": Path("data/design_portal/design_portal_output_contract.json"),
    "buildability_validation": Path("data/validation/buildability_viability_manufacturability_validation.json"),
    "internet_readiness": Path("data/internet_readiness/internet_readiness_verification.json"),
    "update_pack_staging": Path("data/update_packs/update_pack_staging_index.json"),
    "rollback_plan": Path("data/update_packs/rollback_plan_index.json"),
    "runner_gate": Path("data/update_packs/automatic_update_runner_gate.json"),
    "regression_lock": Path("data/update_packs/update_governance_regression_lock.json"),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def summarize(value: Any, limit: int = 420) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value[:limit] + ("..." if len(value) > limit else "")
    try:
        text = json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    return text[:limit] + ("..." if len(text) > limit else "")


def get_nested(data: Dict[str, Any], path: list[str], default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def unwrap_runtime_truth(runtime_truth: Dict[str, Any], dashboard_runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    candidates = [runtime_truth, dashboard_runtime_truth]
    for item in candidates:
        if not isinstance(item, dict) or not item:
            continue
        if isinstance(item.get("runtime_truth"), dict):
            merged = dict(item)
            merged.update(item["runtime_truth"])
            return merged
        if isinstance(item.get("dashboard_runtime_truth"), dict):
            merged = dict(item)
            merged.update(item["dashboard_runtime_truth"])
            return merged
        return item
    return {}


def surface_from_truth(truth: Dict[str, Any], name: str, label: str, description: str = "") -> Dict[str, Any]:
    surfaces = truth.get("surfaces") if isinstance(truth.get("surfaces"), dict) else {}
    aliases = {
        "signal_basis": ["signal", "signals"],
        "trend_discovery": ["trend", "trends"],
        "thesis": ["insight", "thesis"],
        "discovery": ["discovery", "discovery_generation"],
        "breakthrough": ["breakthrough", "innovation"],
        "advancement_path": ["advancement_path", "path_selection"],
        "portfolio": ["portfolio"],
        "strategy": ["strategy"],
        "acquisition": ["acquisition"],
        "final_package": ["final_package", "package"],
        "next_actions": ["next_actions", "actions"],
    }

    if name in surfaces and isinstance(surfaces[name], dict):
        item = surfaces[name]
        status = item.get("status") or ("present" if item.get("raw_available") else "missing")
        summary = item.get("summary") or item.get("value") or item.get("status")
        return {
            "key": name,
            "label": label,
            "status": status,
            "value": summarize(summary) if summary else ("Loaded from runtime truth." if status != "missing" else "Not loaded"),
            "description": description,
        }

    for key in [name] + aliases.get(name, []):
        value = truth.get(key)
        if value not in (None, "", [], {}):
            return {
                "key": name,
                "label": label,
                "status": "present",
                "value": summarize(value),
                "description": description,
            }

    return {
        "key": name,
        "label": label,
        "status": "missing",
        "value": "Not loaded",
        "description": description,
    }


def status_from_bool(present: bool) -> str:
    return "present" if present else "missing"


def latest_count(index: Dict[str, Any], key: str) -> int:
    items = index.get(key)
    return len(items) if isinstance(items, list) else 0


def build_operator_dashboard_state(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    payloads: Dict[str, Dict[str, Any]] = {}
    sources: Dict[str, Dict[str, Any]] = {}
    for name, path in INPUTS.items():
        payload, source = read_json(root / path)
        payloads[name] = payload
        sources[name] = source

    truth = unwrap_runtime_truth(payloads["runtime_truth"], payloads["dashboard_runtime_truth"])
    proof = payloads["proof_pack"]
    stop_go = payloads["stop_go"]
    route_audit = payloads["route_audit"]
    autodesign = payloads["autodesign_handoff"]
    design_portal = payloads["design_portal"]
    buildability = payloads["buildability_validation"]
    internet = payloads["internet_readiness"]
    update_staging = payloads["update_pack_staging"]
    rollback = payloads["rollback_plan"]
    runner_gate = payloads["runner_gate"]
    regression_lock = payloads["regression_lock"]

    runtime_loaded = bool(truth)
    proof_loaded = bool(proof)
    route_contract = route_audit.get("contract") if isinstance(route_audit.get("contract"), dict) else {}
    stop_go_status = stop_go.get("status") or proof.get("status") or "not_loaded"

    route_selected = route_contract.get("selected_route") or get_nested(truth, ["route", "selected"]) or truth.get("selected_route") or "not_loaded"
    route_family = route_contract.get("route_family") or get_nested(truth, ["route", "family"]) or "not_loaded"

    state = {
        "contract_version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "backend": {
            "online": True,
            "message": "Backend is serving operator dashboard state.",
        },
        "source": {
            "runtime_truth_loaded": runtime_loaded,
            "proof_pack_loaded": proof_loaded,
            "missing_data_stays_missing": True,
            "inputs": sources,
        },
        "mission": {
            "title": get_nested(truth, ["mission", "title"]) or truth.get("title") or "Claire Syntalion Operator Cockpit",
            "status": stop_go_status,
            "summary": get_nested(proof, ["stop_go", "recommendation"]) or "Start a run or rebuild runtime truth to populate live mission data.",
        },
        "scorecards": {
            "backend": {"label": "Backend", "value": "Online", "status": "present"},
            "runtime_truth": {"label": "Runtime Truth", "value": "Loaded" if runtime_loaded else "Missing", "status": status_from_bool(runtime_loaded)},
            "route": {"label": "Route", "value": route_family, "status": status_from_bool(route_family != "not_loaded")},
            "autodesign": {
                "label": "AutoDesign",
                "value": get_nested(autodesign, ["route", "handoff_status"], "not_loaded"),
                "status": status_from_bool(bool(autodesign)),
            },
            "internet": {
                "label": "Internet",
                "value": internet.get("status", "not_loaded"),
                "status": status_from_bool(bool(internet)),
            },
            "updates": {
                "label": "Updates",
                "value": get_nested(regression_lock, ["lock_state", "status"], "Guarded"),
                "status": status_from_bool(bool(regression_lock)),
            },
        },
        "route_gate": {
            "status": route_contract.get("status") or "not_loaded",
            "selected_route": route_selected,
            "route_family": route_family,
            "terminal_state": route_contract.get("terminal_state") or truth.get("terminal_state") or "not_loaded",
            "invention_required": bool(route_contract.get("invention_required")),
            "summary": "Actual route surfaces are loaded from runtime truth, route audit, and proof contracts.",
        },
        "surfaces": {
            "signal_basis": surface_from_truth(truth, "signal_basis", "Signal Basis"),
            "trend_discovery": surface_from_truth(truth, "trend_discovery", "Trend Discovery"),
            "thesis": surface_from_truth(truth, "thesis", "Thesis"),
            "discovery": surface_from_truth(truth, "discovery", "Discovery"),
            "breakthrough": surface_from_truth(truth, "breakthrough", "Breakthrough"),
            "advancement_path": surface_from_truth(truth, "advancement_path", "Advancement Path"),
            "portfolio": surface_from_truth(truth, "portfolio", "Portfolio"),
            "strategy": surface_from_truth(truth, "strategy", "Strategy"),
            "acquisition": surface_from_truth(truth, "acquisition", "Acquisition"),
            "final_package": surface_from_truth(truth, "final_package", "Final Package"),
            "next_actions": surface_from_truth(truth, "next_actions", "Next Actions"),
        },
        "autodesign": {
            "status": get_nested(autodesign, ["route", "handoff_status"], "missing" if not autodesign else "present"),
            "required": bool(get_nested(autodesign, ["route", "invention_required"], False)),
            "problem_statement": summarize(get_nested(autodesign, ["autodesign_request", "problem_statement"])) or "Not loaded",
            "invention_need": summarize(get_nested(autodesign, ["autodesign_request", "invention_need"])) or "Not loaded",
            "design_portal_required": bool(get_nested(autodesign, ["autodesign_request", "design_portal_required"], False)),
        },
        "design_portal": {
            "status": design_portal.get("status", "missing" if not design_portal else "present"),
            "architecture_summary": summarize(get_nested(design_portal, ["sections", "architecture_summary"])) or "Not loaded",
            "blueprint_summary": summarize(get_nested(design_portal, ["sections", "blueprint_summary"])) or "Not loaded",
            "component_map": summarize(get_nested(design_portal, ["sections", "component_map"])) or "Not loaded",
            "technology_stack": summarize(get_nested(design_portal, ["sections", "technology_stack"])) or "Not loaded",
            "package_readiness": summarize(get_nested(design_portal, ["sections", "package_readiness"])) or "Not loaded",
        },
        "buildability": {
            "status": buildability.get("status", "missing" if not buildability else "present"),
            "dimensions": buildability.get("dimensions", {}),
            "blockers": buildability.get("blockers", []),
            "warnings": buildability.get("warnings", []),
            "readiness": buildability.get("readiness", {}),
        },
        "internet": {
            "status": internet.get("status", "missing" if not internet else "present"),
            "mode": internet.get("mode", "not_loaded"),
            "readiness": internet.get("readiness", {}),
            "blockers": internet.get("blockers", []),
            "warnings": internet.get("warnings", []),
        },
        "updates": {
            "status": get_nested(regression_lock, ["lock_state", "status"], "missing" if not regression_lock else "present"),
            "staged_pack_count": latest_count(update_staging, "packs"),
            "rollback_plan_count": latest_count(rollback, "plans"),
            "runner_gate": get_nested(runner_gate, ["gate_state", "status"], "not_loaded"),
            "regression_lock_active": bool(get_nested(regression_lock, ["lock_state", "regression_lock_active"], False)),
            "automatic_updates_enabled": False,
            "background_execution_enabled": False,
            "execution_enabled": False,
        },
        "proof": {
            "status": proof.get("status", stop_go_status),
            "stop_go": proof.get("stop_go") or stop_go,
            "domain_status": {
                name: item.get("status")
                for name, item in (proof.get("domains") if isinstance(proof.get("domains"), dict) else {}).items()
                if isinstance(item, dict)
            },
            "launch_readiness": proof.get("launch_readiness", {}),
        },
        "actions": [
            {"label": "Refresh Runtime Truth", "method": "GET", "path": "/operator/dashboard/state"},
            {"label": "Rebuild Runtime Truth", "method": "POST", "path": "/runtime/truth/rebuild"},
            {"label": "Route Audit", "method": "GET", "path": "/routes/audit"},
            {"label": "Proof Pack", "method": "GET", "path": "/proof/e2e"},
            {"label": "Stop/Go", "method": "GET", "path": "/system/stop-go"},
        ],
    }

    write_json(root / STATE_PATH, state)
    return state


def operator_dashboard_state_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    state = build_operator_dashboard_state(project_root)
    return {
        "contract_version": VERSION,
        "generated_at": now(),
        "backend": state.get("backend"),
        "mission": state.get("mission"),
        "route_gate": state.get("route_gate"),
        "scorecards": state.get("scorecards"),
        "proof_status": state.get("proof", {}).get("status"),
    }
