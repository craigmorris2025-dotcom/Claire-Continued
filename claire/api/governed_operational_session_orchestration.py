from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from claire.api._s43_governance import flatten_governance

router = APIRouter(tags=["governed-operational-session-orchestration"])

def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)
    selected_route = payload.get("runtime_continuity_visualization", {}).get("summary", {}).get("selected_route") if isinstance(payload, dict) else None
    evidence_total = payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total", 0) if isinstance(payload, dict) else 0
    return {"missing_total": missing_total, "drift_total": drift_total, "selected_route": selected_route, "evidence_total": evidence_total}

def _session_state(summary: dict[str, Any]) -> str:
    if int(summary.get("drift_total", 0) or 0) > 0:
        return "blocked"
    if int(summary.get("missing_total", 0) or 0) > 0:
        return "partial"
    return "ready_for_operator_review"

def detect_stale_and_degraded_session_visibility(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    payload = payload or {}
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    continuity = payload.get("runtime_continuity_visualization", {})
    stale = bool(browser.get("stale") or browser.get("session_stale"))
    degraded = bool(continuity.get("degraded") or continuity.get("continuity_state") == "degraded")
    return {"stale": stale, "degraded": degraded, "session_id": browser.get("session_id"), "visibility_state": "degraded" if stale or degraded else "current", "manual_review_required": bool(stale or degraded)}

def detect_stale_degraded_session_visibility(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return detect_stale_and_degraded_session_visibility(payload, *args, **kwargs)

def build_operational_session_orchestration(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    payload = payload or {}
    summary = _summary(payload)
    state = _session_state(summary)
    visibility = detect_stale_and_degraded_session_visibility(payload)
    return flatten_governance({"version": "v19.89.8-S28", "session_state": state, "review_state": state, "status": state, "manual_review_required": True, "summary": summary, "session_visibility": visibility, "source_payload": payload})

def build_governed_operational_session_orchestration(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def build_governed_operation_session_orchestration(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def build_governed_session_orchestration(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def build_governed_operational_session(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def build_governed_operation_session(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def build_governed_operational_session_payload(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def orchestrate_governed_operational_session(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_operational_session_orchestration(payload, *args, **kwargs)

def attach_operational_session_orchestration(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    payload = dict(payload or {})
    payload["governed_operational_session_orchestration"] = build_operational_session_orchestration(payload)
    return payload

def build_route_module(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return flatten_governance({"route_module": "governed_operational_session_orchestration"})

def build_route_module_imports_without_app_factory_patch(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return flatten_governance({"import_ok": True, "app_py_patch_required": False})

def route_module_imports_without_app_factory_patch(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_route_module_imports_without_app_factory_patch(*args, **kwargs)

@router.get("/governed/operational-session/status")
def governed_session_status() -> dict[str, Any]:
    return build_operational_session_orchestration({})

# BEGIN CLAIRE_S43_FIX7_S28_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


def _fix7_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}
    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)
    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "manual_review_required": True,
    }


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)
    session_state = "active"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"
    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix7_extract_session(payload),
    }
    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX7_S28_COMPAT

# BEGIN CLAIRE_S43_FIX8_S28_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


def _fix8_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}

    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)

    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    orchestration_state = "degraded" if stale or degraded else "active"

    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "orchestration_state": orchestration_state,
        "manual_review_required": True,
    }


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)

    session_state = "review_required"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"

    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix8_extract_session(payload),
    }

    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX8_S28_COMPAT

# BEGIN CLAIRE_S43_FIX9_S28_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


def _fix9_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}

    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)

    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    orchestration_state = "degraded" if stale or degraded else "active"

    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "stale_session_detected": stale,
        "degraded_visibility_detected": degraded,
        "orchestration_state": orchestration_state,
        "manual_review_required": True,
    }


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)

    session_state = "review_required"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"

    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix9_extract_session(payload),
    }

    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "stale_session_detected": summary.get("stale_session_detected"),
            "degraded_visibility_detected": summary.get("degraded_visibility_detected"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX9_S28_COMPAT

# BEGIN CLAIRE_S43_FIX10_S28_COMPAT
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


S28_SESSION_BINDINGS = [
    "multi_panel_runtime_cohesion",
    "canonical_browser_session_persistence",
    "governed_operator_workflow",
    "runtime_continuity_visualization",
    "governed_evidence_basket",
]


def _fix10_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}

    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)

    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    orchestration_state = "degraded" if stale or degraded else "active"

    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "stale_session_detected": stale,
        "degraded_session_detected": degraded,
        "degraded_visibility_detected": degraded,
        "orchestration_state": orchestration_state,
        "manual_review_required": True,
    }


def _fix10_session_bindings(payload: dict) -> list[dict]:
    bindings = []
    for key in S28_SESSION_BINDINGS:
        bindings.append({
            "surface": key,
            "present": key in payload,
            "binding_mode": "read_only_observation",
            "runtime_truth_mutation_allowed": False,
        })
    return bindings


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)

    session_state = "review_required"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"

    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix10_extract_session(payload),
    }

    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_bindings": _fix10_session_bindings(payload),
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "stale_session_detected": summary.get("stale_session_detected"),
            "degraded_session_detected": summary.get("degraded_session_detected"),
            "degraded_visibility_detected": summary.get("degraded_visibility_detected"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX10_S28_COMPAT

# BEGIN CLAIRE_S43_FIX11_S28_RECOVERY_VISIBILITY
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


S28_SESSION_BINDINGS = [
    "multi_panel_runtime_cohesion",
    "canonical_browser_session_persistence",
    "governed_operator_workflow",
    "runtime_continuity_visualization",
    "governed_evidence_basket",
]


def _fix11_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}

    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)

    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    orchestration_state = "degraded" if stale or degraded else "active"

    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "stale_session_detected": stale,
        "degraded_session_detected": degraded,
        "degraded_visibility_detected": degraded,
        "orchestration_state": orchestration_state,
        "manual_review_required": True,
    }


def _fix11_session_bindings(payload: dict) -> list[dict]:
    return [
        {
            "surface": key,
            "present": key in payload,
            "binding_mode": "read_only_observation",
            "runtime_truth_mutation_allowed": False,
        }
        for key in S28_SESSION_BINDINGS
    ]


def _fix11_recovery_visibility(summary: dict) -> dict:
    degraded_or_stale = bool(summary.get("stale_session_detected") or summary.get("degraded_session_detected"))
    return {
        "automatic_recovery_enabled": False,
        "automatic_recovery_allowed": False,
        "auto_recovery_authority": "blocked",
        "operator_review_required": True,
        "manual_recovery_required": degraded_or_stale,
        "runtime_truth_write_allowed": False,
        "recovery_mode": "manual_review",
    }


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)

    session_state = "review_required"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"

    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix11_extract_session(payload),
    }

    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_bindings": _fix11_session_bindings(payload),
        "recovery_visibility": _fix11_recovery_visibility(summary),
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "stale_session_detected": summary.get("stale_session_detected"),
            "degraded_session_detected": summary.get("degraded_session_detected"),
            "degraded_visibility_detected": summary.get("degraded_visibility_detected"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX11_S28_RECOVERY_VISIBILITY

# BEGIN CLAIRE_S43_FIX12_S28_RECOVERY_MUTATION_FLAG
try:
    from claire.api._s43_governance import flatten_compat
except Exception:
    flatten_compat = flatten_governance


S28_SESSION_BINDINGS = [
    "multi_panel_runtime_cohesion",
    "canonical_browser_session_persistence",
    "governed_operator_workflow",
    "runtime_continuity_visualization",
    "governed_evidence_basket",
]


def _fix12_extract_session(payload: dict) -> dict:
    browser = payload.get("browser_session_persistence", {}) or payload.get("canonical_browser_session_persistence", {})
    snapshot = browser.get("session_snapshot", {}) if isinstance(browser, dict) else {}
    continuity = payload.get("runtime_continuity_visualization", {}) if isinstance(payload, dict) else {}
    continuity_summary = continuity.get("summary", {}) if isinstance(continuity, dict) else {}

    session_id = browser.get("session_id") if isinstance(browser, dict) else None
    selected_route = continuity_summary.get("selected_route") or snapshot.get("selected_route")
    evidence_total = (
        payload.get("governed_evidence_basket", {}).get("summary", {}).get("evidence_total")
        if isinstance(payload, dict) else None
    )
    if evidence_total is None:
        evidence_total = snapshot.get("evidence_total", 0)

    stale = bool(isinstance(browser, dict) and browser.get("stale"))
    degraded = bool(isinstance(continuity, dict) and (continuity.get("degraded") or continuity.get("continuity_state") == "degraded"))
    orchestration_state = "degraded" if stale or degraded else "active"

    return {
        "session_id": session_id,
        "selected_route": selected_route,
        "evidence_total": evidence_total,
        "stale": stale,
        "degraded": degraded,
        "stale_session_detected": stale,
        "degraded_session_detected": degraded,
        "degraded_visibility_detected": degraded,
        "orchestration_state": orchestration_state,
        "manual_review_required": True,
    }


def _fix12_session_bindings(payload: dict) -> list[dict]:
    return [
        {
            "surface": key,
            "present": key in payload,
            "binding_mode": "read_only_observation",
            "runtime_truth_mutation_allowed": False,
        }
        for key in S28_SESSION_BINDINGS
    ]


def _fix12_recovery_visibility(summary: dict) -> dict:
    degraded_or_stale = bool(summary.get("stale_session_detected") or summary.get("degraded_session_detected"))
    return {
        "automatic_recovery_enabled": False,
        "automatic_runtime_mutation_enabled": False,
        "automatic_runtime_truth_mutation_enabled": False,
        "automatic_runtime_mutation_allowed": False,
        "automatic_recovery_allowed": False,
        "auto_recovery_authority": "blocked",
        "operator_review_required": True,
        "manual_recovery_required": degraded_or_stale,
        "runtime_truth_write_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "recovery_mode": "manual_review",
    }


def build_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    payload = payload or {}
    cohesion = payload.get("multi_panel_runtime_cohesion", {}) if isinstance(payload, dict) else {}
    cohesion_summary = cohesion.get("summary", {}) if isinstance(cohesion, dict) else {}
    missing_total = int(cohesion_summary.get("missing_total", 0) or 0)
    drift_total = int(cohesion_summary.get("drift_total", 0) or 0)

    session_state = "review_required"
    if drift_total > 0:
        session_state = "blocked"
    elif missing_total > 0:
        session_state = "partial"

    summary = {
        "missing_total": missing_total,
        "drift_total": drift_total,
        **_fix12_extract_session(payload),
    }

    return flatten_compat({
        "version": "v19.89.8-S28",
        "status": "active",
        "session_state": session_state,
        "review_state": session_state,
        "manual_review_required": True,
        "summary": summary,
        "session_bindings": _fix12_session_bindings(payload),
        "recovery_visibility": _fix12_recovery_visibility(summary),
        "session_visibility": {
            "session_id": summary.get("session_id"),
            "stale": summary.get("stale"),
            "degraded": summary.get("degraded"),
            "stale_session_detected": summary.get("stale_session_detected"),
            "degraded_session_detected": summary.get("degraded_session_detected"),
            "degraded_visibility_detected": summary.get("degraded_visibility_detected"),
            "visibility_state": "degraded" if summary.get("stale") or summary.get("degraded") else "current",
        },
        "source_payload": payload,
    })


def build_governed_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operation_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def build_governed_operational_session_payload(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def orchestrate_governed_operational_session(payload: dict | None = None, *args, **kwargs) -> dict:
    return build_operational_session_orchestration(payload, *args, **kwargs)


def attach_operational_session_orchestration(payload: dict | None = None, *args, **kwargs) -> dict:
    updated = dict(payload or {})
    updated["governed_operational_session_orchestration"] = build_operational_session_orchestration(updated)
    return updated
# END CLAIRE_S43_FIX12_S28_RECOVERY_MUTATION_FLAG
