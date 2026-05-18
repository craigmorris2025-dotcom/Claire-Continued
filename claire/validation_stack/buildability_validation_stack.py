
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.69"
CONTRACT_NAME = "Buildability / Viability / Manufacturability Validation Stack"

DESIGN_PORTAL_PATH = Path("data/design_portal/design_portal_output_contract.json")
AUTODESIGN_HANDOFF_PATH = Path("data/autodesign/autodesign_handoff_contract.json")
RUNTIME_TRUTH_PATH = Path("data/runtime/runtime_truth_canonical.json")
ROUTE_AUDIT_PATH = Path("data/routes/discovery_breakthrough_innovation_route_audit.json")

OUTPUT_PATH = Path("data/validation/buildability_viability_manufacturability_validation.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/buildability_validation_payload.json")

VALIDATION_DIMENSIONS = [
    "buildability",
    "viability",
    "manufacturability_deployability",
    "technical_feasibility",
    "evidence_readiness",
    "dependency_readiness",
    "implementation_readiness",
    "package_readiness",
]

REQUIRED_DESIGN_SECTIONS = [
    "architecture_summary",
    "blueprint_summary",
    "component_map",
    "dependency_map",
    "technology_stack",
    "implementation_plan",
    "buildability_requirements",
    "validation_requirements",
    "risks",
    "evidence_trace",
    "package_readiness",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


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


def summarize(value: Any, limit: int = 900) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        text = str(value)
        return text[:limit] + ("..." if len(text) > limit else "")
    if isinstance(value, list):
        return value[:25]
    if isinstance(value, dict):
        return {key: summarize(item, 450) for key, item in list(value.items())[:35]}
    return str(value)[:limit]


def get_nested(data: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def section_available(design_contract: Dict[str, Any], section: str) -> bool:
    sections = design_contract.get("sections") if isinstance(design_contract.get("sections"), dict) else {}
    value = sections.get(section)
    if value in (None, "", [], {}):
        return False
    status = None
    if isinstance(value, dict):
        status = str(value.get("status") or "").lower()
    if status in {"missing", "blocked", "blocked_missing_handoff", "failed"}:
        return False
    return True


def assess_design_input(design_contract: Dict[str, Any]) -> Dict[str, Any]:
    missing = [section for section in REQUIRED_DESIGN_SECTIONS if not section_available(design_contract, section)]
    status = design_contract.get("status", "missing")
    route = design_contract.get("route", {})
    governance = design_contract.get("governance", {})
    return {
        "design_status": status,
        "route": route,
        "missing_design_sections": missing,
        "design_contract_available": bool(design_contract),
        "no_fake_blueprints": governance.get("no_fake_blueprints") is True,
        "buildability_validation_required": governance.get("buildability_validation_required") is True,
    }


def score_dimension(name: str, design_contract: Dict[str, Any], handoff: Dict[str, Any], runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    sections = design_contract.get("sections") if isinstance(design_contract.get("sections"), dict) else {}
    route = design_contract.get("route") if isinstance(design_contract.get("route"), dict) else {}
    handoff_route = handoff.get("route") if isinstance(handoff.get("route"), dict) else {}
    runtime_route = runtime_truth.get("route") if isinstance(runtime_truth.get("route"), dict) else {}

    evidence = []
    blockers = []
    warnings = []
    required_next = []

    if name == "buildability":
        architecture = sections.get("architecture_summary")
        components = sections.get("component_map")
        dependencies = sections.get("dependency_map")
        implementation = sections.get("implementation_plan")
        if architecture:
            evidence.append("architecture_summary_present")
        else:
            blockers.append("architecture_summary_missing")
        if components:
            evidence.append("component_map_present")
        else:
            blockers.append("component_map_missing")
        if dependencies:
            evidence.append("dependency_map_present")
        else:
            blockers.append("dependency_map_missing")
        if implementation:
            evidence.append("implementation_plan_present")
        else:
            blockers.append("implementation_plan_missing")
        required_next.append("Detailed AutoDesign-generated component and dependency proof")

    elif name == "viability":
        validation = sections.get("validation_requirements")
        risks = sections.get("risks")
        evidence_trace = sections.get("evidence_trace")
        if validation:
            evidence.append("validation_requirements_present")
        else:
            blockers.append("validation_requirements_missing")
        if risks:
            evidence.append("risks_present")
        else:
            warnings.append("risk_register_missing")
        if evidence_trace:
            evidence.append("evidence_trace_present")
        else:
            blockers.append("evidence_trace_missing")
        required_next.append("Operator review of viability assumptions")

    elif name == "manufacturability_deployability":
        stack = sections.get("technology_stack")
        dependencies = sections.get("dependency_map")
        if stack:
            evidence.append("technology_stack_present")
        else:
            blockers.append("technology_stack_missing")
        if dependencies:
            evidence.append("dependency_map_present")
        else:
            blockers.append("dependency_map_missing")
        required_next.append("Deployment/manufacturing constraints must be proven before package readiness")

    elif name == "technical_feasibility":
        stack = sections.get("technology_stack")
        buildability_requirements = sections.get("buildability_requirements")
        if stack:
            evidence.append("technology_stack_present")
        else:
            blockers.append("technology_stack_missing")
        if buildability_requirements:
            evidence.append("buildability_requirements_present")
        else:
            blockers.append("buildability_requirements_missing")
        route_invention = bool(route.get("invention_required") or handoff_route.get("invention_required") or runtime_route.get("invention_required"))
        if route_invention:
            warnings.append("invention_route_requires_higher_feasibility_threshold")
        required_next.append("Prototype or architecture proof may be required")

    elif name == "evidence_readiness":
        runtime_evidence = get_nested(runtime_truth, ["surfaces", "evidence", "raw_available"])
        validation_surface = get_nested(runtime_truth, ["surfaces", "validation", "raw_available"])
        evidence_trace = sections.get("evidence_trace")
        if runtime_evidence or evidence_trace:
            evidence.append("evidence_available")
        else:
            blockers.append("evidence_missing")
        if validation_surface:
            evidence.append("runtime_validation_surface_available")
        else:
            warnings.append("runtime_validation_surface_missing")
        required_next.append("Evidence trace must support any build-readiness claim")

    elif name == "dependency_readiness":
        dependency_map = sections.get("dependency_map")
        stack = sections.get("technology_stack")
        if dependency_map:
            evidence.append("dependency_map_present")
        else:
            blockers.append("dependency_map_missing")
        if stack:
            evidence.append("technology_stack_present")
        else:
            warnings.append("technology_stack_missing")
        required_next.append("Dependencies must be classified as known, unknown, blocker, or optional")

    elif name == "implementation_readiness":
        implementation = sections.get("implementation_plan")
        package = sections.get("package_readiness")
        if implementation:
            evidence.append("implementation_plan_present")
        else:
            blockers.append("implementation_plan_missing")
        if package:
            evidence.append("package_readiness_present")
        else:
            warnings.append("package_readiness_missing")
        required_next.append("Implementation phases must be validated against constraints")

    elif name == "package_readiness":
        package = sections.get("package_readiness")
        if isinstance(package, dict):
            if package.get("ready_for_final_package") is True:
                evidence.append("ready_for_final_package_true")
            else:
                warnings.append("package_not_ready_for_final_package")
            if package.get("requires_v17_69_validation") is True:
                evidence.append("v17_69_validation_required_flag_present")
        else:
            blockers.append("package_readiness_missing")
        required_next.append("Package readiness remains false until validation passes")

    if blockers:
        status = "blocked"
    elif warnings:
        status = "warning"
    else:
        status = "passed"

    return {
        "dimension": name,
        "status": status,
        "evidence": evidence,
        "warnings": warnings,
        "blockers": blockers,
        "required_next": required_next,
    }


def overall_status(dimensions: Dict[str, Dict[str, Any]], design_input: Dict[str, Any]) -> str:
    if not design_input["design_contract_available"]:
        return "blocked_missing_design_portal_contract"
    if any(item["status"] == "blocked" for item in dimensions.values()):
        return "blocked"
    if any(item["status"] == "warning" for item in dimensions.values()):
        return "warning"
    return "passed"


def build_validation_stack(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    design_contract, design_source = read_json(root / DESIGN_PORTAL_PATH)
    handoff, handoff_source = read_json(root / AUTODESIGN_HANDOFF_PATH)
    runtime_truth, runtime_source = read_json(root / RUNTIME_TRUTH_PATH)
    route_audit, route_audit_source = read_json(root / ROUTE_AUDIT_PATH)

    design_input = assess_design_input(design_contract)

    dimensions = {
        name: score_dimension(name, design_contract, handoff, runtime_truth)
        for name in VALIDATION_DIMENSIONS
    }

    status = overall_status(dimensions, design_input)

    blockers = []
    warnings = []
    for item in dimensions.values():
        blockers.extend(item.get("blockers", []))
        warnings.extend(item.get("warnings", []))

    if design_input["missing_design_sections"]:
        warnings.append("Design Portal contract missing sections: " + ", ".join(design_input["missing_design_sections"]))

    validation = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": status,
        "sources": {
            "design_portal": design_source,
            "autodesign_handoff": handoff_source,
            "runtime_truth": runtime_source,
            "route_audit": route_audit_source,
        },
        "route": design_input.get("route"),
        "design_input": design_input,
        "dimensions": dimensions,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "readiness": {
            "build_ready": status == "passed",
            "package_ready": False,
            "requires_operator_review": True,
            "requires_internet_readiness_before_live_updates": True,
            "requires_update_governance_before_automatic_updates": True,
        },
        "governance": {
            "no_fake_validation": True,
            "missing_inputs_remain_visible": True,
            "build_readiness_requires_all_dimensions_passed": True,
            "operator_review_required": True,
            "autodesign_design_portal_outputs_required_for_invention_routes": True,
        },
        "next": [
            "v17.70 Internet Readiness Verification",
            "v17.71-v17.74 Governed update-pack staging and rollback-aware automatic update preparation",
            "v17.75 Full end-to-end proof pack",
        ],
    }

    write_json(root / OUTPUT_PATH, validation)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": validation["generated_at"],
        "status": validation["status"],
        "route": validation["route"],
        "dimensions": validation["dimensions"],
        "blockers": validation["blockers"],
        "warnings": validation["warnings"],
        "readiness": validation["readiness"],
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return validation


def validation_stack_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    validation = build_validation_stack(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": validation.get("status"),
        "route": validation.get("route"),
        "readiness": validation.get("readiness"),
        "blockers": validation.get("blockers", []),
        "warnings": validation.get("warnings", []),
    }
