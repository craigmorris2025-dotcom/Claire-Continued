from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from .evidence_traceability import build_evidence_traceability_index
from .validation_report import (
    ValidationCheck,
    compute_score,
    fail_check,
    final_status,
    pass_check,
    utc_now,
    warn_check,
)


ALLOWED_STAGE_STATUSES: Set[str] = {
    "pending",
    "running",
    "completed",
    "skipped_by_route",
    "blocked",
    "failed",
    "not_applicable",
}

CANONICAL_TERMINAL_STATES: Set[str] = {
    "trend_thesis_ready",
    "portfolio_action_ready",
    "portfolio_optimization_ready",
    "discovery_ready",
    "breakthrough_classified",
    "advancement_path_selected",
    "design_output_ready",
    "acquisition_package_ready",
    "acquisition_ready",
    "final_package_ready",
    "insufficient_data",
    "blocked",
    "failed",
    "max_iterations_reached",
}

ROUTE_REQUIRED_STAGES: Dict[str, List[int]] = {
    "portfolio": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 26, 27],
    "portfolio_optimization": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 26, 27],
    "breakthrough": list(range(1, 23)),
    "autodesign": list(range(1, 23)),
    "design": list(range(1, 23)),
    "system_design": list(range(1, 23)),
    "acquisition": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 24, 25, 28, 29, 30],
    "package": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 23, 24, 25, 26, 28, 29, 30],
    "insufficient_data": [1, 2, 3],
}

ROUTE_TERMINAL_FIT: Dict[str, Set[str]] = {
    "portfolio": {"portfolio_action_ready", "portfolio_optimization_ready"},
    "portfolio_optimization": {"portfolio_action_ready", "portfolio_optimization_ready"},
    "breakthrough": {"breakthrough_classified", "advancement_path_selected", "design_output_ready", "discovery_ready"},
    "autodesign": {"design_output_ready", "advancement_path_selected"},
    "design": {"design_output_ready", "advancement_path_selected"},
    "system_design": {"design_output_ready", "advancement_path_selected"},
    "acquisition": {"acquisition_ready", "acquisition_package_ready", "final_package_ready"},
    "package": {"final_package_ready", "acquisition_package_ready"},
    "insufficient_data": {"insufficient_data"},
}


def _truth_section(runtime_truth: Dict[str, Any], name: str) -> Dict[str, Any]:
    value = runtime_truth.get(name)
    return value if isinstance(value, dict) else {}


def _first_present(mapping: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return default


def _normalize_route(route: Any) -> str:
    if not route:
        return "unknown"
    route_text = str(route).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "auto_design": "autodesign",
        "design_portal": "design",
        "final_package": "package",
        "acquisition_package": "acquisition",
    }
    return aliases.get(route_text, route_text)


def _stage_number(stage: Dict[str, Any]) -> Optional[int]:
    raw = _first_present(stage, ["stage_number", "number", "id", "stage_id"])
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if digits:
            try:
                return int(digits)
            except ValueError:
                return None
    return None


def _stage_status(stage: Dict[str, Any]) -> str:
    raw = _first_present(stage, ["status", "stage_status"], "pending")
    return str(raw).strip().lower()


def _extract_stages(runtime_truth: Dict[str, Any]) -> List[Dict[str, Any]]:
    stage_truth = _truth_section(runtime_truth, "stage_truth")
    stages = stage_truth.get("stages")
    if stages is None:
        stages = runtime_truth.get("stages")
    if isinstance(stages, dict):
        return [stage for stage in stages.values() if isinstance(stage, dict)]
    if isinstance(stages, list):
        return [stage for stage in stages if isinstance(stage, dict)]
    return []


def _route_from_truth(runtime_truth: Dict[str, Any]) -> str:
    route_truth = _truth_section(runtime_truth, "route_truth")
    run_truth = _truth_section(runtime_truth, "run_truth")
    return _normalize_route(
        _first_present(route_truth, ["route_selected", "selected_route", "route"], None)
        or _first_present(run_truth, ["selected_route", "route_selected", "route"], None)
        or runtime_truth.get("route_selected")
    )


def _terminal_from_truth(runtime_truth: Dict[str, Any]) -> str:
    terminal_truth = _truth_section(runtime_truth, "terminal_truth")
    run_truth = _truth_section(runtime_truth, "run_truth")
    return str(
        _first_present(terminal_truth, ["terminal_state", "state"], None)
        or _first_present(run_truth, ["terminal_state"], None)
        or runtime_truth.get("terminal_state")
        or ""
    ).strip()


def _runtime_validation_passed(runtime_truth: Dict[str, Any]) -> Optional[bool]:
    validation_truth = _truth_section(runtime_truth, "validation_truth")
    raw = _first_present(validation_truth, ["validation_passed", "passed", "is_valid"], None)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        lowered = raw.lower().strip()
        if lowered in {"true", "pass", "passed", "valid", "yes"}:
            return True
        if lowered in {"false", "fail", "failed", "invalid", "no"}:
            return False
    return None


class ValidationAuthority:
    """Evaluate runtime truth and produce a deterministic validation authority report."""

    contract_version = "claire.validation_authority.v17.60"

    def evaluate(self, runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
        checks: List[ValidationCheck] = []
        checks.extend(self._check_required_truth_sections(runtime_truth))
        checks.extend(self._check_run_truth(runtime_truth))
        checks.extend(self._check_stage_truth(runtime_truth))
        checks.extend(self._check_route_truth(runtime_truth))
        checks.extend(self._check_terminal_truth(runtime_truth))
        checks.extend(self._check_evidence_truth(runtime_truth))
        checks.extend(self._check_memory_truth(runtime_truth))

        evidence_index = build_evidence_traceability_index(runtime_truth)
        status = final_status(checks)
        score = compute_score(checks)
        route = _route_from_truth(runtime_truth)
        terminal = _terminal_from_truth(runtime_truth)

        run_truth = _truth_section(runtime_truth, "run_truth")
        run_id = _first_present(run_truth, ["run_id", "id"], runtime_truth.get("run_id") or "unknown")

        critical_failures = [
            check.to_dict() for check in checks
            if check.status == "fail" and check.severity == "critical"
        ]
        blocking_failures = [
            check.to_dict() for check in checks
            if check.status == "fail" and check.severity in {"critical", "high"}
        ]

        memory_eligible = status == "pass"

        return {
            "schema": "claire.validation_authority_report.v1",
            "contract_version": self.contract_version,
            "generated_at": utc_now(),
            "run_id": run_id,
            "route_selected": route,
            "terminal_state": terminal or "missing",
            "validation_authority_status": status,
            "validation_passed": status == "pass",
            "validation_score": score,
            "memory_eligible": memory_eligible,
            "recursive_feedback_allowed": memory_eligible,
            "checks_total": len(checks),
            "checks_passed": len([c for c in checks if c.status == "pass"]),
            "checks_warning": len([c for c in checks if c.status == "warning"]),
            "checks_failed": len([c for c in checks if c.status == "fail"]),
            "critical_failures": critical_failures,
            "blocking_failures": blocking_failures,
            "evidence_summary": {
                "evidence_count": evidence_index.get("evidence_count", 0),
                "unsupported_count": evidence_index.get("unsupported_count", 0),
                "stages_with_evidence": len(evidence_index.get("by_stage", {})),
                "routes_with_evidence": len(evidence_index.get("by_route", {})),
                "source_type_count": len(evidence_index.get("by_source_type", {})),
            },
            "checks": [check.to_dict() for check in checks],
        }

    def _check_required_truth_sections(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        required = [
            "run_truth",
            "stage_truth",
            "route_truth",
            "terminal_truth",
            "validation_truth",
            "evidence_truth",
            "memory_truth",
            "runtime_health_truth",
        ]

        missing = [section for section in required if section not in runtime_truth]
        if missing:
            checks.append(fail_check(
                "truth.required_sections",
                "Runtime truth sections present",
                f"Missing truth sections: {', '.join(missing)}",
                "Run tools/claire_build_runtime_truth.py, then rerun tools/claire_validate_runtime_truth.py.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "truth.required_sections",
                "Runtime truth sections present",
                "All required v17.59 runtime truth sections are present.",
            ))

        return checks

    def _check_run_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        run_truth = _truth_section(runtime_truth, "run_truth")
        run_id = _first_present(run_truth, ["run_id", "id"], runtime_truth.get("run_id"))
        status = _first_present(run_truth, ["status", "run_status"], None)

        if run_id:
            checks.append(pass_check("run.run_id", "Run ID present", f"Run ID: {run_id}"))
        else:
            checks.append(fail_check(
                "run.run_id",
                "Run ID present",
                "No run_id was found in runtime truth.",
                "Ensure the runtime writes run_id into core_run_output.json and dashboard_runtime_truth.json.",
                severity="critical",
            ))

        if status:
            checks.append(pass_check("run.status", "Run status present", f"Run status: {status}"))
        else:
            checks.append(warn_check(
                "run.status",
                "Run status present",
                "Run status is missing.",
                "Expose idle/running/completed/failed/blocked status in run_truth.",
            ))

        return checks

    def _check_stage_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        stages = _extract_stages(runtime_truth)

        if not stages:
            return [fail_check(
                "stage.present",
                "Stage truth present",
                "No stage list found.",
                "runtime_truth.stage_truth.stages must contain all 30 lifecycle stages.",
                severity="critical",
            )]

        stage_by_number: Dict[int, Dict[str, Any]] = {}
        invalid_statuses: List[str] = []

        for stage in stages:
            number = _stage_number(stage)
            status = _stage_status(stage)
            if number is not None:
                stage_by_number[number] = stage
            if status not in ALLOWED_STAGE_STATUSES:
                invalid_statuses.append(f"{number or '?'}:{status}")

        missing_stage_numbers = [number for number in range(1, 31) if number not in stage_by_number]
        if missing_stage_numbers:
            checks.append(fail_check(
                "stage.all_30_present",
                "All 30 lifecycle stages present",
                f"Missing stage numbers: {missing_stage_numbers}",
                "The runtime truth builder must emit all 30 stages, even when skipped_by_route or not_applicable.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "stage.all_30_present",
                "All 30 lifecycle stages present",
                "All 30 lifecycle stages are represented.",
            ))

        if invalid_statuses:
            checks.append(fail_check(
                "stage.allowed_statuses",
                "Stage statuses are canonical",
                f"Invalid statuses: {', '.join(invalid_statuses)}",
                f"Allowed statuses: {', '.join(sorted(ALLOWED_STAGE_STATUSES))}.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "stage.allowed_statuses",
                "Stage statuses are canonical",
                "All stage statuses use the canonical status set.",
            ))

        unresolved = [
            number for number, stage in stage_by_number.items()
            if _stage_status(stage) in {"pending", "running"}
        ]
        terminal = _terminal_from_truth(runtime_truth)
        if terminal and unresolved and terminal not in {"insufficient_data", "blocked", "failed", "max_iterations_reached"}:
            checks.append(warn_check(
                "stage.unresolved_with_terminal",
                "Terminal state has resolved stage statuses",
                f"Terminal state exists but these stages remain pending/running: {unresolved[:12]}",
                "Completed runs should resolve every stage to completed, skipped_by_route, blocked, failed, or not_applicable.",
            ))
        else:
            checks.append(pass_check(
                "stage.resolution",
                "Stage resolution compatible with run state",
                "Stage statuses are compatible with the current terminal/run state.",
            ))

        return checks

    def _check_route_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        route = _route_from_truth(runtime_truth)

        if route == "unknown":
            checks.append(fail_check(
                "route.selected",
                "Route selected",
                "No route_selected value was found.",
                "Route gate must write route_selected into route_truth and run_truth.",
                severity="high",
            ))
            return checks

        checks.append(pass_check("route.selected", "Route selected", f"Selected route: {route}"))

        stages = _extract_stages(runtime_truth)
        stage_by_number = {
            _stage_number(stage): stage for stage in stages
            if _stage_number(stage) is not None
        }

        required = ROUTE_REQUIRED_STAGES.get(route)
        if not required:
            checks.append(warn_check(
                "route.contract_known",
                "Route has validation contract",
                f"No built-in route stage contract for route '{route}'.",
                "Add this route to ROUTE_REQUIRED_STAGES in validation_authority.py.",
            ))
            return checks

        missing_required = []
        incomplete_required = []
        for number in required:
            stage = stage_by_number.get(number)
            if stage is None:
                missing_required.append(number)
                continue
            status = _stage_status(stage)
            if status not in {"completed", "skipped_by_route", "not_applicable"}:
                incomplete_required.append(f"{number}:{status}")

        if missing_required or incomplete_required:
            checks.append(fail_check(
                "route.required_stage_fit",
                "Route required stages are resolved",
                f"Missing required stages: {missing_required}; incomplete required stages: {incomplete_required}",
                "The selected route must complete, skip by route, or mark not applicable all route-required stages.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "route.required_stage_fit",
                "Route required stages are resolved",
                f"Required stages for route '{route}' are resolved.",
            ))

        if route in {"breakthrough", "autodesign", "design", "system_design"}:
            design_block = list(range(16, 23))
            bad_design_block = [
                f"{number}:{_stage_status(stage_by_number.get(number, {}))}"
                for number in design_block
                if number not in stage_by_number or _stage_status(stage_by_number.get(number, {})) not in {"completed", "blocked", "failed", "skipped_by_route", "not_applicable"}
            ]
            if bad_design_block:
                checks.append(fail_check(
                    "route.design_block_16_22",
                    "Stages 16–22 are preserved for design routes",
                    f"Stages 16–22 unresolved: {bad_design_block}",
                    "Design-capable routes must explicitly represent stages 16–22.",
                    severity="critical",
                ))
            else:
                checks.append(pass_check(
                    "route.design_block_16_22",
                    "Stages 16–22 are preserved for design routes",
                    "Stages 16–22 are explicitly represented for the selected design-capable route.",
                ))

        return checks

    def _check_terminal_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        terminal = _terminal_from_truth(runtime_truth)
        route = _route_from_truth(runtime_truth)

        if not terminal:
            checks.append(fail_check(
                "terminal.present",
                "Terminal state present",
                "No terminal_state found.",
                "Every completed run must end in a canonical terminal state.",
                severity="critical",
            ))
            return checks

        if terminal not in CANONICAL_TERMINAL_STATES:
            checks.append(fail_check(
                "terminal.canonical",
                "Terminal state is canonical",
                f"Terminal state '{terminal}' is not recognized.",
                f"Use one of: {', '.join(sorted(CANONICAL_TERMINAL_STATES))}.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "terminal.canonical",
                "Terminal state is canonical",
                f"Terminal state: {terminal}",
            ))

        allowed_for_route = ROUTE_TERMINAL_FIT.get(route)
        universal_failure_terminals = {"insufficient_data", "blocked", "failed", "max_iterations_reached"}
        if allowed_for_route and terminal not in allowed_for_route and terminal not in universal_failure_terminals:
            checks.append(warn_check(
                "terminal.route_fit",
                "Terminal state fits selected route",
                f"Terminal '{terminal}' is unusual for route '{route}'. Expected: {sorted(allowed_for_route)}",
                "Confirm route selection and terminal assignment are aligned.",
            ))
        else:
            checks.append(pass_check(
                "terminal.route_fit",
                "Terminal state fits selected route",
                "Terminal state is compatible with selected route or is a valid failure/insufficient-data terminal.",
            ))

        return checks

    def _check_evidence_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        index = build_evidence_traceability_index(runtime_truth)
        evidence_count = index.get("evidence_count", 0)
        unsupported_count = index.get("unsupported_count", 0)

        if evidence_count <= 0:
            checks.append(fail_check(
                "evidence.present",
                "Evidence is present",
                "No evidence items found.",
                "Each run should emit stage-linked evidence or evidence_chain entries.",
                severity="high",
            ))
        else:
            checks.append(pass_check(
                "evidence.present",
                "Evidence is present",
                f"{evidence_count} evidence item(s) found.",
            ))

        if unsupported_count > 0:
            checks.append(warn_check(
                "evidence.supported_claims",
                "Evidence supports explicit claims",
                f"{unsupported_count} evidence item(s) lack a claim_supported/claim/summary value.",
                "Add claim_supported values so evidence can be audited from claim to source.",
            ))
        else:
            checks.append(pass_check(
                "evidence.supported_claims",
                "Evidence supports explicit claims",
                "All evidence items contain an explicit supported claim.",
            ))

        stages_with_evidence = index.get("by_stage", {})
        if evidence_count > 0 and len(stages_with_evidence) <= 1:
            checks.append(warn_check(
                "evidence.stage_coverage",
                "Evidence is linked across stages",
                "Evidence exists but is linked to one or fewer stages.",
                "Attach evidence_id/stage_number pairs across lifecycle stages.",
            ))
        elif evidence_count > 0:
            checks.append(pass_check(
                "evidence.stage_coverage",
                "Evidence is linked across stages",
                f"Evidence is linked across {len(stages_with_evidence)} stage bucket(s).",
            ))

        return checks

    def _check_memory_truth(self, runtime_truth: Dict[str, Any]) -> List[ValidationCheck]:
        checks: List[ValidationCheck] = []
        memory_truth = _truth_section(runtime_truth, "memory_truth")
        runtime_validation = _runtime_validation_passed(runtime_truth)

        raw_memory_eligible = _first_present(memory_truth, ["memory_eligible", "eligible"], False)
        memory_eligible = raw_memory_eligible is True or str(raw_memory_eligible).lower() == "true"

        if runtime_validation is False and memory_eligible:
            checks.append(fail_check(
                "memory.validation_gate",
                "Memory requires validation pass",
                "memory_eligible=true while runtime validation_truth indicates failure.",
                "Set memory_eligible=false unless validation passes.",
                severity="critical",
            ))
        else:
            checks.append(pass_check(
                "memory.validation_gate",
                "Memory requires validation pass",
                "Memory eligibility does not violate the validation gate.",
            ))

        recursive_allowed_raw = _first_present(memory_truth, ["recursive_feedback_allowed", "recursion_allowed"], False)
        recursive_allowed = recursive_allowed_raw is True or str(recursive_allowed_raw).lower() == "true"

        if recursive_allowed and not memory_eligible:
            checks.append(fail_check(
                "memory.recursion_gate",
                "Recursive feedback requires memory eligibility",
                "recursive_feedback_allowed=true while memory_eligible is not true.",
                "Recursive feedback must remain blocked until validation and memory eligibility pass.",
                severity="critical",
            ))
        else:
            checks.append(pass_check(
                "memory.recursion_gate",
                "Recursive feedback requires memory eligibility",
                "Recursive feedback gate is consistent with memory eligibility.",
            ))

        return checks


def build_validation_report(runtime_truth: Dict[str, Any]) -> Dict[str, Any]:
    return ValidationAuthority().evaluate(runtime_truth)
