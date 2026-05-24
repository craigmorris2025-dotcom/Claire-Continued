from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping

from .runtime_truth_contract import first_present, normalize_key


@dataclass
class MemoryTruth:
    memory_eligible: bool
    memory_status: str
    memory_reason: str
    validated_output_required: bool
    stored_at: str
    recursive_feedback_allowed: bool
    raw: Any


def _raw_eligible(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    key = normalize_key(value)
    if key in {"eligible", "true", "yes", "allowed", "approved", "pass", "passed"}:
        return True
    if key in {"ineligible", "false", "no", "blocked", "denied", "fail", "failed"}:
        return False
    return None


def build_memory_truth(raw: Mapping[str, Any], validation_truth: Mapping[str, Any]) -> Dict[str, Any]:
    raw_memory = raw.get("memory") if "memory" in raw else raw.get("memory_eligibility") if "memory_eligibility" in raw else raw.get("recursive_memory")
    memory_obj = raw_memory if isinstance(raw_memory, Mapping) else {}
    requested = _raw_eligible(first_present(memory_obj, ["memory_eligible", "eligible", "eligibility", "recursive_feedback_allowed"], raw_memory))
    validation_passed = bool(validation_truth.get("validation_passed"))
    if validation_passed and requested is not False:
        eligible = True
        status = "eligible"
        reason = "Validation passed and memory was not explicitly denied."
    elif not validation_passed:
        eligible = False
        status = "blocked"
        reason = "No validation pass; verified memory and recursive feedback are blocked."
    else:
        eligible = False
        status = "ineligible"
        reason = "Runtime memory eligibility was explicitly denied."
    return asdict(MemoryTruth(
        memory_eligible=eligible,
        memory_status=status,
        memory_reason=str(first_present(memory_obj, ["memory_reason", "reason"], reason)),
        validated_output_required=True,
        stored_at=str(first_present(memory_obj, ["stored_at", "timestamp"], "not_stored")),
        recursive_feedback_allowed=eligible,
        raw=raw_memory,
    ))
