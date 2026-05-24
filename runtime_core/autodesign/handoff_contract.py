
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.67"
CONTRACT_NAME = "AutoDesign Handoff Contract"

RUNTIME_TRUTH_PATHS = [
    Path("data/runtime/runtime_truth_canonical.json"),
    Path("data/runtime/dashboard_runtime_truth.json"),
    Path("data/dashboard/operator_dashboard_state.json"),
]

ROUTE_AUDIT_PATH = Path("data/routes/discovery_breakthrough_innovation_route_audit.json")
HANDOFF_PATH = Path("data/autodesign/autodesign_handoff_contract.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/autodesign_handoff_payload.json")

HANDOFF_INPUT_SURFACES = [
    "signal_basis",
    "trend_discovery",
    "thesis",
    "discovery",
    "breakthrough",
    "advancement_path",
    "technology_intelligence",
    "validation",
    "evidence",
    "failures",
]

REQUIRED_WHEN_INVENTION = [
    "discovery",
    "breakthrough",
    "advancement_path",
]

DESIGN_OUTPUT_REQUIREMENTS = [
    "problem_statement",
    "invention_need",
    "solution_concept",
    "system_type",
    "intended_function",
    "component_targets",
    "technology_stack_constraints",
    "buildability_questions",
    "validation_questions",
    "design_portal_required",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> Tuple[Optional[Any], Optional[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_first_valid(root: Path, paths: List[Path]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    attempts = []
    for relative in paths:
        path = root / relative
        if not path.exists():
            attempts.append({"path": str(relative).replace("\\", "/"), "status": "missing"})
            continue
        payload, error = read_json(path)
        if error or not isinstance(payload, dict):
            attempts.append({"path": str(relative).replace("\\", "/"), "status": "invalid", "error": error})
            continue
        attempts.append({"path": str(relative).replace("\\", "/"), "status": "loaded"})
        return payload, {"selected": str(relative).replace("\\", "/"), "attempts": attempts}
    return {}, {"selected": None, "attempts": attempts}


def unwrap_truth(payload: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(payload.get("runtime_truth"), dict):
        merged = dict(payload)
        merged.update(payload["runtime_truth"])
        return merged
    if isinstance(payload.get("dashboard_runtime_truth"), dict):
        merged = dict(payload)
        merged.update(payload["dashboard_runtime_truth"])
        return merged
    if isinstance(payload.get("core_run_output"), dict):
        merged = dict(payload)
        merged.update(payload["core_run_output"])
        return merged
    return payload


def selected_route(truth: Dict[str, Any], audit: Dict[str, Any]) -> str:
    contract = audit.get("contract") if isinstance(audit.get("contract"), dict) else {}
    if contract.get("selected_route"):
        return str(contract["selected_route"])
    route = truth.get("route")
    if isinstance(route, dict):
        return str(route.get("selected") or route.get("route") or route.get("name") or "unknown")
    for key in ["route_selected", "selected_route", "active_route"]:
        if truth.get(key):
            return str(truth[key])
    return str(route or "unknown")


def route_family(truth: Dict[str, Any], audit: Dict[str, Any]) -> str:
    contract = audit.get("contract") if isinstance(audit.get("contract"), dict) else {}
    if contract.get("route_family"):
        return str(contract["route_family"])
    route = selected_route(truth, audit).lower()
    if any(token in route for token in ["autodesign", "auto_design", "solution", "design", "invention", "system"]):
        return "autodesign"
    if any(token in route for token in ["breakthrough", "innovation", "advancement"]):
        return "breakthrough"
    if "portfolio" in route:
        return "portfolio"
    if "acquisition" in route or "package" in route:
        return "acquisition"
    if "discovery" in route or "thesis" in route:
        return "discovery"
    return "unknown"


def invention_required(truth: Dict[str, Any], audit: Dict[str, Any]) -> bool:
    contract = audit.get("contract") if isinstance(audit.get("contract"), dict) else {}
    if contract.get("invention_required") is True:
        return True
    route = truth.get("route") if isinstance(truth.get("route"), dict) else {}
    if route.get("invention_required") is True or route.get("autodesign_required") is True:
        return True
    selected = selected_route(truth, audit).lower()
    return any(token in selected for token in ["design", "solution", "invention", "breakthrough", "innovation", "system"])


def get_surface(truth: Dict[str, Any], name: str) -> Dict[str, Any]:
    surfaces = truth.get("surfaces") if isinstance(truth.get("surfaces"), dict) else {}
    if name in surfaces and isinstance(surfaces[name], dict):
        item = surfaces[name]
        return {
            "name": name,
            "status": item.get("status", "present"),
            "available": bool(item.get("raw_available") or item.get("status") not in (None, "", "missing")),
            "summary": item.get("summary") if "summary" in item else item.get("value"),
            "source": item.get("source_key", "surfaces"),
        }

    aliases = {
        "autodesign": ["auto_design", "auto_invention", "solution"],
        "design_portal": ["design_output", "blueprint"],
        "trend_discovery": ["trend"],
        "signal_basis": ["signal"],
    }
    keys = [name] + aliases.get(name, [])
    for key in keys:
        if truth.get(key) not in (None, ""):
            return {
                "name": name,
                "status": "present",
                "available": True,
                "summary": truth.get(key),
                "source": key,
            }
    return {"name": name, "status": "missing", "available": False, "summary": None, "source": None}


def summarize_text(value: Any, limit: int = 700) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value[:limit] + ("..." if len(value) > limit else "")
    try:
        text = json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    return text[:limit] + ("..." if len(text) > limit else "")


def derive_problem_statement(inputs: Dict[str, Dict[str, Any]], route: str) -> str:
    for key in ["discovery", "breakthrough", "thesis", "trend_discovery"]:
        summary = inputs.get(key, {}).get("summary")
        if summary:
            return summarize_text(summary, 600)
    if route and route != "unknown":
        return f"Route '{route}' requires AutoDesign review, but the discovery summary is incomplete."
    return "AutoDesign problem statement is not available yet."


def derive_invention_need(inputs: Dict[str, Dict[str, Any]], route: str, family: str) -> str:
    advancement = inputs.get("advancement_path", {}).get("summary")
    breakthrough = inputs.get("breakthrough", {}).get("summary")
    if advancement:
        return summarize_text(advancement, 650)
    if breakthrough:
        return summarize_text(breakthrough, 650)
    return f"Determine whether the {family} route requires a new technology, system design, product architecture, or buildable solution."


def assess_handoff_status(required: bool, missing_inputs: List[str], autodesign_existing: bool, design_portal_existing: bool) -> str:
    if not required:
        return "not_required"
    if missing_inputs:
        return "required_missing_inputs"
    if autodesign_existing and design_portal_existing:
        return "already_satisfied"
    if autodesign_existing and not design_portal_existing:
        return "autodesign_present_design_portal_needed"
    return "handoff_ready"


def build_autodesign_handoff(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    runtime_payload, runtime_source = load_first_valid(root, RUNTIME_TRUTH_PATHS)
    runtime_truth = unwrap_truth(runtime_payload) if runtime_payload else {}

    route_audit, audit_source = load_first_valid(root, [ROUTE_AUDIT_PATH])

    route = selected_route(runtime_truth, route_audit)
    family = route_family(runtime_truth, route_audit)
    required = invention_required(runtime_truth, route_audit)

    inputs = {name: get_surface(runtime_truth, name) for name in HANDOFF_INPUT_SURFACES}
    autodesign_surface = get_surface(runtime_truth, "autodesign")
    design_portal_surface = get_surface(runtime_truth, "design_portal")
    technology_surface = get_surface(runtime_truth, "technology_intelligence")

    missing_required_inputs = []
    if required:
        for item in REQUIRED_WHEN_INVENTION:
            if not inputs.get(item, {}).get("available"):
                missing_required_inputs.append(item)

    handoff_status = assess_handoff_status(
        required=required,
        missing_inputs=missing_required_inputs,
        autodesign_existing=autodesign_surface["available"],
        design_portal_existing=design_portal_surface["available"],
    )

    problem_statement = derive_problem_statement(inputs, route)
    invention_need = derive_invention_need(inputs, route, family)

    handoff = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "source": {
            "runtime_truth": runtime_source,
            "route_audit": audit_source,
        },
        "route": {
            "selected": route,
            "family": family,
            "invention_required": required,
            "handoff_status": handoff_status,
        },
        "handoff_inputs": inputs,
        "existing_outputs": {
            "autodesign": autodesign_surface,
            "design_portal": design_portal_surface,
            "technology_intelligence": technology_surface,
        },
        "autodesign_request": {
            "required": required,
            "status": handoff_status,
            "problem_statement": problem_statement,
            "invention_need": invention_need,
            "solution_concept": "pending_autodesign_generation" if required and not autodesign_surface["available"] else autodesign_surface.get("summary"),
            "system_type": "to_be_selected_by_autodesign",
            "intended_function": "to_be_derived_from_discovery_and_advancement_path",
            "component_targets": [],
            "technology_stack_constraints": technology_surface.get("summary"),
            "buildability_questions": [
                "What must be built for this discovery to become a viable solution?",
                "Which components, dependencies, data, models, interfaces, or infrastructure are required?",
                "What evidence is still missing before design output can be trusted?",
            ],
            "validation_questions": [
                "Is the concept technically feasible?",
                "Is the route supported by evidence?",
                "Is the design deployable or manufacturable?",
                "Should the output proceed to Design Portal?",
            ],
            "design_portal_required": required,
        },
        "required_design_output_contract": DESIGN_OUTPUT_REQUIREMENTS,
        "missing_required_inputs": missing_required_inputs,
        "failures": [],
        "warnings": [],
        "governance": {
            "no_fake_autodesign_output": True,
            "missing_inputs_remain_missing": True,
            "operator_review_required": True,
            "design_portal_required_for_invention_routes": True,
        },
        "next": [
            "v17.68 Design Portal Output Contract",
            "v17.69 Buildability / Viability / Manufacturability Validation Stack",
        ],
    }

    if required and missing_required_inputs:
        handoff["warnings"].append("AutoDesign handoff is required but missing route inputs.")
    if required and not autodesign_surface["available"]:
        handoff["warnings"].append("AutoDesign output is not present yet. Handoff request is ready for generation.")
    if required and not design_portal_surface["available"]:
        handoff["warnings"].append("Design Portal output is not present yet. v17.68 must enforce the Design Portal output contract.")

    write_json(root / HANDOFF_PATH, handoff)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": handoff["generated_at"],
        "route": handoff["route"],
        "autodesign_request": handoff["autodesign_request"],
        "missing_required_inputs": handoff["missing_required_inputs"],
        "warnings": handoff["warnings"],
        "existing_outputs": handoff["existing_outputs"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return handoff


def autodesign_handoff_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    handoff = build_autodesign_handoff(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "route": handoff.get("route"),
        "status": handoff.get("route", {}).get("handoff_status"),
        "required": handoff.get("autodesign_request", {}).get("required"),
        "missing_required_inputs": handoff.get("missing_required_inputs", []),
        "warnings": handoff.get("warnings", []),
    }
