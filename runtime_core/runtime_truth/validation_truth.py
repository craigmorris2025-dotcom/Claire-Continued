from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping

from .runtime_truth_contract import first_present, normalize_key, now_utc


@dataclass
class ValidationTruth:
    validation_status: str
    validation_passed: bool
    validation_score: float | None
    checks_passed: List[str]
    checks_failed: List[str]
    contract_errors: List[str]
    evidence_errors: List[str]
    route_integrity_errors: List[str]
    confidence_threshold_errors: List[str]
    validated_at: str
    validator_version: str
    raw: Any


def _status_from_raw(value: Any) -> str:
    if isinstance(value, bool):
        return "pass" if value else "fail"
    key = normalize_key(value)
    if key in {"pass", "passed", "valid", "validated", "true", "success", "ok"}:
        return "pass"
    if key in {"fail", "failed", "invalid", "false", "error"}:
        return "fail"
    if key in {"running", "pending", "in_progress"}:
        return "pending"
    return "unverified"


def _score(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        score = float(value)
        return max(0.0, min(1.0, score if score <= 1 else score / 100.0))
    except Exception:
        return None


def build_validation_truth(raw: Mapping[str, Any], route_truth: Mapping[str, Any], terminal_truth: Mapping[str, Any], evidence_truth: List[Mapping[str, Any]], memory_raw: Any) -> Dict[str, Any]:
    raw_validation = raw.get("validation_result") if "validation_result" in raw else raw.get("validation") if "validation" in raw else raw.get("output_validation")
    validation_obj = raw_validation if isinstance(raw_validation, Mapping) else {}
    status = _status_from_raw(first_present(validation_obj, ["status", "validation_status", "result", "passed", "pass"], raw_validation))
    score = _score(first_present(validation_obj, ["validation_score", "score", "confidence"], None))
    passed: List[str] = []
    failed: List[str] = []

    def check(name: str, condition: bool):
        (passed if condition else failed).append(name)

    check("route_selected", route_truth.get("route_selected") not in {None, "", "not_reported"})
    check("terminal_state_present", terminal_truth.get("terminal_state") not in {None, "", "not_reported"})
    check("terminal_is_final", bool(terminal_truth.get("is_final")))
    check("terminal_fits_route", bool(route_truth.get("route_terminal_fit")) or terminal_truth.get("terminal_type") == "failure")
    check("required_stage_truth_resolved", not bool(route_truth.get("route_missing_stages")) and not bool(route_truth.get("route_blocked_stages")))
    check("evidence_chain_present", bool(evidence_truth))
    check("validation_status_reported", status in {"pass", "fail"})

    raw_contract_errors = first_present(validation_obj, ["contract_errors", "errors.contract", "errors"], [])
    raw_evidence_errors = first_present(validation_obj, ["evidence_errors", "errors.evidence"], [])
    raw_route_errors = first_present(validation_obj, ["route_integrity_errors", "errors.route"], [])
    raw_conf_errors = first_present(validation_obj, ["confidence_threshold_errors", "errors.confidence"], [])

    def as_list(x: Any) -> List[str]:
        if x is None:
            return []
        if isinstance(x, list):
            return [str(v) for v in x]
        return [str(x)]

    contract_errors = as_list(raw_contract_errors)
    evidence_errors = as_list(raw_evidence_errors)
    route_errors = as_list(raw_route_errors)
    confidence_errors = as_list(raw_conf_errors)

    # Computed gate: explicit pass is respected only when structural checks also pass.
    validation_passed = status == "pass" and not failed and not contract_errors and not evidence_errors and not route_errors and not confidence_errors
    if status == "pass" and not validation_passed:
        route_errors.append("raw validation reported pass but runtime truth contract checks failed")

    return asdict(ValidationTruth(
        validation_status=status,
        validation_passed=validation_passed,
        validation_score=score,
        checks_passed=passed,
        checks_failed=failed,
        contract_errors=contract_errors,
        evidence_errors=evidence_errors,
        route_integrity_errors=route_errors,
        confidence_threshold_errors=confidence_errors,
        validated_at=str(first_present(validation_obj, ["validated_at", "timestamp"], now_utc() if validation_passed else "not_validated")),
        validator_version=str(first_present(validation_obj, ["validator_version", "version"], "v17.59_runtime_truth_backbone")),
        raw=raw_validation,
    ))
