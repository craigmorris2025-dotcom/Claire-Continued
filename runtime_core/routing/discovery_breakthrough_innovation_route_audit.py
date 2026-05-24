
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.66"
AUDIT_NAME = "Discovery / Breakthrough / Innovation Route Audit"

RUNTIME_TRUTH_PATHS = [
    Path("data/runtime/runtime_truth_canonical.json"),
    Path("data/runtime/dashboard_runtime_truth.json"),
    Path("data/dashboard/operator_dashboard_state.json"),
]

AUDIT_PATH = Path("data/routes/discovery_breakthrough_innovation_route_audit.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/discovery_breakthrough_innovation_route_payload.json")

ROUTE_FAMILIES = {
    "portfolio": ["portfolio", "portfolio_action", "portfolio_optimization"],
    "discovery": ["discovery", "trend", "thesis", "signal"],
    "breakthrough": ["breakthrough", "innovation", "gap", "advancement"],
    "autodesign": ["autodesign", "auto_design", "auto_invention", "solution", "design", "system"],
    "design_portal": ["design_portal", "design_output", "blueprint", "architecture", "spec"],
    "acquisition": ["acquisition", "package", "final_package", "acquirer"],
}

REQUIRED_SURFACES_BY_ROUTE = {
    "portfolio": ["signal_basis", "trend_discovery", "thesis", "portfolio"],
    "discovery": ["signal_basis", "trend_discovery", "thesis", "discovery"],
    "breakthrough": ["discovery", "breakthrough", "advancement_path"],
    "autodesign": ["discovery", "breakthrough", "advancement_path", "autodesign", "design_portal"],
    "design_portal": ["autodesign", "design_output", "design_portal", "technology_intelligence"],
    "acquisition": ["strategy", "acquisition", "final_package"],
}

FIRST_CLASS_SURFACES = [
    "signal_basis",
    "trend_discovery",
    "thesis",
    "discovery",
    "breakthrough",
    "advancement_path",
    "autodesign",
    "design_output",
    "design_portal",
    "technology_intelligence",
    "portfolio",
    "strategy",
    "acquisition",
    "final_package",
    "validation",
    "evidence",
    "next_actions",
    "failures",
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


def load_best_runtime_truth(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    attempts = []
    for relative in RUNTIME_TRUTH_PATHS:
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


def get_surface_status(truth: Dict[str, Any], surface: str) -> Dict[str, Any]:
    surfaces = truth.get("surfaces") if isinstance(truth.get("surfaces"), dict) else {}
    if surface in surfaces and isinstance(surfaces[surface], dict):
        item = surfaces[surface]
        return {
            "surface": surface,
            "status": item.get("status", "present"),
            "available": bool(item.get("raw_available") or item.get("status") not in (None, "", "missing")),
            "source": "surfaces",
        }

    aliases = {
        "autodesign": ["auto_design", "auto_invention", "solution"],
        "design_portal": ["design_output", "blueprint"],
        "trend_discovery": ["trend"],
        "signal_basis": ["signal"],
        "final_package": ["package"],
    }
    keys = [surface] + aliases.get(surface, [])
    for key in keys:
        if truth.get(key) not in (None, ""):
            return {"surface": surface, "status": "present", "available": True, "source": key}
    return {"surface": surface, "status": "missing", "available": False, "source": None}


def selected_route(truth: Dict[str, Any]) -> str:
    route = truth.get("route")
    if isinstance(route, dict):
        return str(route.get("selected") or route.get("route") or route.get("name") or "unknown")
    for key in ["route_selected", "selected_route", "active_route"]:
        if truth.get(key):
            return str(truth[key])
    return str(route or "unknown")


def terminal_state(truth: Dict[str, Any]) -> str:
    mission = truth.get("mission") if isinstance(truth.get("mission"), dict) else {}
    route = truth.get("route") if isinstance(truth.get("route"), dict) else {}
    for value in [
        truth.get("terminal_state"),
        truth.get("status"),
        mission.get("status"),
        route.get("terminal_state"),
    ]:
        if value:
            return str(value)
    return "unknown"


def infer_route_family(route: str, truth: Dict[str, Any]) -> str:
    lower = route.lower()
    for family, tokens in ROUTE_FAMILIES.items():
        if any(token in lower for token in tokens):
            return family

    availability = {
        surface: get_surface_status(truth, surface)["available"]
        for surface in FIRST_CLASS_SURFACES
    }
    if availability.get("autodesign") or availability.get("design_portal"):
        return "autodesign"
    if availability.get("breakthrough") or availability.get("advancement_path"):
        return "breakthrough"
    if availability.get("portfolio"):
        return "portfolio"
    if availability.get("acquisition") or availability.get("final_package"):
        return "acquisition"
    if availability.get("discovery") or availability.get("thesis"):
        return "discovery"
    return "unknown"


def route_requires_invention(route: str, family: str, truth: Dict[str, Any]) -> bool:
    route_info = truth.get("route") if isinstance(truth.get("route"), dict) else {}
    if route_info.get("invention_required") is True or route_info.get("autodesign_required") is True:
        return True
    lower = route.lower()
    if any(token in lower for token in ["design", "solution", "invention", "breakthrough", "innovation", "system"]):
        return True
    return family in {"autodesign", "design_portal"}


def assess_route_contract(truth: Dict[str, Any]) -> Dict[str, Any]:
    route = selected_route(truth)
    terminal = terminal_state(truth)
    family = infer_route_family(route, truth)
    invention_required = route_requires_invention(route, family, truth)

    required = list(REQUIRED_SURFACES_BY_ROUTE.get(family, []))
    if invention_required:
        for item in ["autodesign", "design_portal", "technology_intelligence"]:
            if item not in required:
                required.append(item)

    first_class = {
        surface: get_surface_status(truth, surface)
        for surface in FIRST_CLASS_SURFACES
    }

    missing_required = [
        surface for surface in required
        if not first_class.get(surface, {}).get("available")
    ]

    warnings = []
    failures = []

    if family == "unknown":
        warnings.append("Selected route family could not be inferred from runtime truth.")

    if invention_required and not first_class["autodesign"]["available"]:
        failures.append("Route requires invention/design, but AutoDesign output is missing.")
    if invention_required and not first_class["design_portal"]["available"]:
        failures.append("Route requires invention/design, but Design Portal output is missing.")
    if family in {"breakthrough", "autodesign", "design_portal"} and not first_class["breakthrough"]["available"]:
        warnings.append("Breakthrough/innovation route appears active, but breakthrough classification is missing.")
    if family in {"breakthrough", "autodesign", "design_portal"} and not first_class["advancement_path"]["available"]:
        warnings.append("Breakthrough/innovation route appears active, but advancement path is missing.")
    if family == "portfolio" and not first_class["portfolio"]["available"]:
        failures.append("Portfolio route inferred, but portfolio output is missing.")

    status = "passed"
    if failures:
        status = "failed"
    elif warnings or missing_required:
        status = "warning"

    return {
        "status": status,
        "selected_route": route,
        "terminal_state": terminal,
        "route_family": family,
        "invention_required": invention_required,
        "required_surfaces": required,
        "missing_required_surfaces": missing_required,
        "first_class_surfaces": first_class,
        "warnings": warnings,
        "failures": failures,
    }


def build_route_audit(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    loaded, source = load_best_runtime_truth(root)
    truth = unwrap_truth(loaded) if loaded else {}
    contract = assess_route_contract(truth)

    audit = {
        "version": VERSION,
        "audit_name": AUDIT_NAME,
        "generated_at": now(),
        "source": source,
        "contract": contract,
        "route_rule": {
            "discovery_breakthrough_innovation_first_class": True,
            "autodesign_required_when_invention_required": True,
            "design_portal_required_when_invention_required": True,
            "portfolio_default_is_preserved": True,
            "missing_outputs_are_not_faked": True,
        },
        "next": [
            "v17.67 AutoDesign Handoff Contract",
            "v17.68 Design Portal Output Contract",
            "v17.69 Buildability / Viability / Manufacturability Validation Stack",
        ],
    }

    write_json(root / AUDIT_PATH, audit)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": audit["generated_at"],
        "route": contract["selected_route"],
        "route_family": contract["route_family"],
        "status": contract["status"],
        "invention_required": contract["invention_required"],
        "missing_required_surfaces": contract["missing_required_surfaces"],
        "warnings": contract["warnings"],
        "failures": contract["failures"],
        "first_class_surfaces": contract["first_class_surfaces"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)
    return audit


def route_audit_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    audit = build_route_audit(project_root)
    contract = audit.get("contract", {})
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": contract.get("status"),
        "route": contract.get("selected_route"),
        "route_family": contract.get("route_family"),
        "invention_required": contract.get("invention_required"),
        "missing_required_surfaces": contract.get("missing_required_surfaces", []),
        "warnings": contract.get("warnings", []),
        "failures": contract.get("failures", []),
    }
