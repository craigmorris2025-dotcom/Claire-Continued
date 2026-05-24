
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.68"
CONTRACT_NAME = "Design Portal Output Contract"

HANDOFF_PATH = Path("data/autodesign/autodesign_handoff_contract.json")
RUNTIME_TRUTH_PATH = Path("data/runtime/runtime_truth_canonical.json")
ROUTE_AUDIT_PATH = Path("data/routes/discovery_breakthrough_innovation_route_audit.json")

OUTPUT_PATH = Path("data/design_portal/design_portal_output_contract.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/design_portal_output_payload.json")

REQUIRED_OUTPUT_SECTIONS = [
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

REQUIRED_FOR_INVENTION_ROUTE = [
    "problem_statement",
    "invention_need",
    "solution_concept",
    "system_type",
    "intended_function",
    "technology_stack_constraints",
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


def load_optional(root: Path, relative: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    path = root / relative
    if not path.exists():
        return {}, {"path": str(relative).replace("\\", "/"), "status": "missing"}
    payload, error = read_json(path)
    if error or not isinstance(payload, dict):
        return {}, {"path": str(relative).replace("\\", "/"), "status": "invalid", "error": error}
    return payload, {"path": str(relative).replace("\\", "/"), "status": "loaded"}


def summarize(value: Any, limit: int = 1000) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        text = str(value)
        return text[:limit] + ("..." if len(text) > limit else "")
    if isinstance(value, list):
        return value[:30]
    if isinstance(value, dict):
        return {key: summarize(item, 500) for key, item in list(value.items())[:40]}
    return str(value)[:limit]


def get_nested(data: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def handoff_route(handoff: Dict[str, Any]) -> Dict[str, Any]:
    route = handoff.get("route") if isinstance(handoff.get("route"), dict) else {}
    return {
        "selected": route.get("selected", "unknown"),
        "family": route.get("family", "unknown"),
        "invention_required": bool(route.get("invention_required")),
        "handoff_status": route.get("handoff_status", "unknown"),
    }


def get_autodesign_request(handoff: Dict[str, Any]) -> Dict[str, Any]:
    request = handoff.get("autodesign_request")
    return request if isinstance(request, dict) else {}


def section_status(value: Any) -> str:
    if value is None or value == "":
        return "missing"
    if isinstance(value, list):
        return "present" if value else "empty"
    if isinstance(value, dict):
        if value.get("status"):
            return str(value["status"])
        return "present" if value else "empty"
    return "present"


def build_component_targets(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    targets = request.get("component_targets")
    if isinstance(targets, list) and targets:
        return [
            {
                "name": str(item.get("name") if isinstance(item, dict) else item),
                "status": "provided",
                "source": "autodesign_handoff",
            }
            for item in targets[:30]
        ]

    return [
        {"name": "core_system_component", "status": "pending_autodesign_detail", "source": "contract_default"},
        {"name": "data_or_signal_interface", "status": "pending_autodesign_detail", "source": "contract_default"},
        {"name": "validation_and_evidence_layer", "status": "pending_autodesign_detail", "source": "contract_default"},
        {"name": "operator_review_surface", "status": "pending_autodesign_detail", "source": "contract_default"},
    ]


def build_dependency_map(request: Dict[str, Any], runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    technology_constraints = request.get("technology_stack_constraints")
    evidence = get_nested(runtime_truth, ["surfaces", "evidence", "summary"])
    validation = get_nested(runtime_truth, ["surfaces", "validation", "summary"])
    return {
        "technology_constraints": summarize(technology_constraints),
        "evidence_dependencies": summarize(evidence),
        "validation_dependencies": summarize(validation),
        "missing_dependency_notes": [
            "Exact implementation dependencies must be generated by AutoDesign or supplied by the selected route output.",
            "Design Portal may not fabricate dependencies when AutoDesign inputs are missing.",
        ],
    }


def build_technology_stack(request: Dict[str, Any], runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    technology_constraints = request.get("technology_stack_constraints")
    technology_truth = get_nested(runtime_truth, ["surfaces", "technology_intelligence", "summary"])
    return {
        "selected_stack": summarize(technology_constraints or technology_truth),
        "selection_status": "provided" if technology_constraints or technology_truth else "pending_technology_intelligence",
        "compatibility_required": True,
        "deployment_assessment_required": True,
        "manufacturability_assessment_required": True,
    }


def determine_status(handoff: Dict[str, Any], request: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    route = handoff_route(handoff)
    warnings: List[str] = []
    failures: List[str] = []

    if not handoff:
        failures.append("AutoDesign handoff contract is missing. Run v17.67 first.")
        return "blocked_missing_handoff", warnings, failures

    if not route["invention_required"]:
        return "not_required_for_current_route", warnings, failures

    missing = []
    for key in REQUIRED_FOR_INVENTION_ROUTE:
        if request.get(key) in (None, "", [], {}):
            missing.append(key)

    if missing:
        warnings.append("AutoDesign handoff is missing required inputs: " + ", ".join(missing))

    if route["handoff_status"] in {"required_missing_inputs"}:
        warnings.append("AutoDesign handoff reports missing inputs. Design Portal output remains contract-level until inputs are supplied.")

    if route["handoff_status"] in {"already_satisfied", "autodesign_present_design_portal_needed", "handoff_ready"}:
        return "contract_ready", warnings, failures

    return "contract_pending", warnings, failures


def build_design_portal_output(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()

    handoff, handoff_source = load_optional(root, HANDOFF_PATH)
    runtime_truth, runtime_source = load_optional(root, RUNTIME_TRUTH_PATH)
    route_audit, route_audit_source = load_optional(root, ROUTE_AUDIT_PATH)

    request = get_autodesign_request(handoff)
    route = handoff_route(handoff)

    output_status, warnings, failures = determine_status(handoff, request)

    problem_statement = request.get("problem_statement")
    invention_need = request.get("invention_need")
    solution_concept = request.get("solution_concept")
    system_type = request.get("system_type")
    intended_function = request.get("intended_function")

    architecture_summary = {
        "status": "ready_for_review" if output_status == "contract_ready" else output_status,
        "problem_statement": summarize(problem_statement),
        "invention_need": summarize(invention_need),
        "solution_concept": summarize(solution_concept),
        "system_type": summarize(system_type),
        "intended_function": summarize(intended_function),
        "route": route,
    }

    blueprint_summary = {
        "status": "contract_defined" if output_status in {"contract_ready", "contract_pending"} else output_status,
        "blueprint_level": "conceptual_to_implementation_ready_after_autodesign_details",
        "must_include": [
            "architecture summary",
            "component map",
            "dependency map",
            "technology stack",
            "implementation phases",
            "validation gates",
            "risk and blocker register",
        ],
    }

    component_map = {
        "status": "pending_detail" if not request.get("component_targets") else "provided",
        "components": build_component_targets(request),
    }

    dependency_map = build_dependency_map(request, runtime_truth)
    technology_stack = build_technology_stack(request, runtime_truth)

    implementation_plan = {
        "status": "contract_defined",
        "phases": [
            {"phase": 1, "name": "Confirm route evidence and invention need", "required": True},
            {"phase": 2, "name": "Generate detailed AutoDesign architecture", "required": route.get("invention_required", False)},
            {"phase": 3, "name": "Map components, dependencies, and stack", "required": True},
            {"phase": 4, "name": "Run buildability / viability / manufacturability validation", "required": True},
            {"phase": 5, "name": "Package design output for portfolio, acquisition, or build route", "required": True},
        ],
    }

    buildability_requirements = {
        "status": "required",
        "required_next_build": "v17.69 Buildability / Viability / Manufacturability Validation Stack",
        "questions": request.get("buildability_questions") or [
            "Can this architecture be built with available technologies?",
            "What components and dependencies are blockers?",
            "What evidence is required before build claim confidence increases?",
        ],
    }

    validation_requirements = {
        "status": "required",
        "questions": request.get("validation_questions") or [
            "Is the design technically feasible?",
            "Is the invention route evidence-backed?",
            "Does it require prototype validation?",
            "Is it deployable or manufacturable?",
        ],
    }

    risks = {
        "status": "active",
        "items": [
            "Do not treat contract-level Design Portal output as a completed blueprint.",
            "Do not proceed to automatic build/update without validation gates.",
            "Do not hide missing AutoDesign inputs.",
        ] + warnings + failures,
    }

    evidence_trace = {
        "runtime_truth_source": runtime_source,
        "route_audit_source": route_audit_source,
        "autodesign_handoff_source": handoff_source,
        "route_audit_status": get_nested(route_audit, ["contract", "status"]),
        "route_audit_family": get_nested(route_audit, ["contract", "route_family"]),
    }

    package_readiness = {
        "status": "not_ready" if output_status.startswith("blocked") else "contract_ready_for_validation",
        "ready_for_final_package": False,
        "requires_v17_69_validation": True,
        "requires_operator_review": True,
    }

    contract = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": output_status,
        "route": route,
        "sources": {
            "runtime_truth": runtime_source,
            "route_audit": route_audit_source,
            "autodesign_handoff": handoff_source,
        },
        "sections": {
            "architecture_summary": architecture_summary,
            "blueprint_summary": blueprint_summary,
            "component_map": component_map,
            "dependency_map": dependency_map,
            "technology_stack": technology_stack,
            "implementation_plan": implementation_plan,
            "buildability_requirements": buildability_requirements,
            "validation_requirements": validation_requirements,
            "risks": risks,
            "evidence_trace": evidence_trace,
            "package_readiness": package_readiness,
        },
        "section_status": {
            key: section_status(value)
            for key, value in {
                "architecture_summary": architecture_summary,
                "blueprint_summary": blueprint_summary,
                "component_map": component_map,
                "dependency_map": dependency_map,
                "technology_stack": technology_stack,
                "implementation_plan": implementation_plan,
                "buildability_requirements": buildability_requirements,
                "validation_requirements": validation_requirements,
                "risks": risks,
                "evidence_trace": evidence_trace,
                "package_readiness": package_readiness,
            }.items()
        },
        "required_output_sections": REQUIRED_OUTPUT_SECTIONS,
        "warnings": warnings,
        "failures": failures,
        "governance": {
            "no_fake_blueprints": True,
            "missing_inputs_remain_visible": True,
            "operator_review_required": True,
            "buildability_validation_required": True,
            "design_portal_is_first_class_route_output": True,
        },
        "next": [
            "v17.69 Buildability / Viability / Manufacturability Validation Stack",
            "v17.70 Internet Readiness Verification",
        ],
    }

    write_json(root / OUTPUT_PATH, contract)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": contract["generated_at"],
        "status": contract["status"],
        "route": contract["route"],
        "sections": contract["sections"],
        "section_status": contract["section_status"],
        "warnings": warnings,
        "failures": failures,
        "package_readiness": package_readiness,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)

    return contract


def design_portal_output_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    contract = build_design_portal_output(project_root)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": contract.get("status"),
        "route": contract.get("route"),
        "section_status": contract.get("section_status"),
        "warnings": contract.get("warnings", []),
        "failures": contract.get("failures", []),
        "package_readiness": contract.get("sections", {}).get("package_readiness"),
    }
