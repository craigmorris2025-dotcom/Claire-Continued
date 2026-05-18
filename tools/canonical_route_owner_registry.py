#!/usr/bin/env python3
"""
Canonical Route Owner Registry

This tool creates and validates Claire's first explicit route authority registry.
It does not mutate FastAPI mounts. It declares intended authority so the next
build can demote duplicate or compatibility owners safely.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "data" / "runtime_authority"
REGISTRY_PATH = REGISTRY_DIR / "canonical_route_owner_registry.json"
REPORT_DIR = ROOT / "audits" / "v19_84_4_canonical_route_owner_registry"
REPORT_JSON = REPORT_DIR / "canonical_route_owner_registry_report.json"
REPORT_MD = REPORT_DIR / "canonical_route_owner_registry_report.md"
V19_84_3_REPORT = ROOT / "audits" / "v19_84_3_canonical_route_mount_audit" / "canonical_route_mount_audit_report.json"

CANONICAL_ROUTE_OWNERS = {
    "/dashboard/payload": {
        "methods": ["GET"],
        "canonical_owner": "backend.enterprise_cockpit_payload_bridge",
        "truth_owner": "backend",
        "cockpit_role": "presentation_only",
        "purpose": "Unified enterprise cockpit payload composed from backend runtime truth.",
        "required_state": "single_owner",
        "compatibility_policy": "no_frontend_synthesis; legacy aliases must delegate to canonical backend payload only",
    },
    "/dashboard/payload/status": {
        "methods": ["GET"],
        "canonical_owner": "backend.enterprise_cockpit_payload_status",
        "truth_owner": "backend",
        "cockpit_role": "presentation_only",
        "purpose": "Health/status check for canonical cockpit payload availability.",
        "required_state": "single_owner",
        "compatibility_policy": "status must report backend truth owner and must not compute cockpit truth",
    },
    "/runtime/continuous/status": {
        "methods": ["GET"],
        "canonical_owner": "backend.continuous_intelligence_runtime_status",
        "truth_owner": "backend",
        "cockpit_role": "presentation_only",
        "purpose": "Governed continuous runtime status, scheduler state, guardrails, and artifact paths.",
        "required_state": "single_owner",
        "compatibility_policy": "manual runs and continuous runtime remain separate",
    },
    "/runtime/continuous/review-queue": {
        "methods": ["GET"],
        "canonical_owner": "backend.continuous_intelligence_review_queue",
        "truth_owner": "backend",
        "cockpit_role": "presentation_only",
        "purpose": "Operator review queue for candidates requiring approval before promotion.",
        "required_state": "single_owner",
        "compatibility_policy": "no promotion without operator review",
    },
    "/runs/start": {
        "methods": ["POST"],
        "canonical_owner": "backend.enterprise_runtime_runs_backend",
        "truth_owner": "backend",
        "cockpit_role": "operator_command",
        "purpose": "Start a governed manual runtime run and create backend-owned run artifacts.",
        "required_state": "single_owner",
        "compatibility_policy": "must initialize pending_evidence rather than fabricate outputs",
    },
    "/universes": {
        "methods": ["GET"],
        "canonical_owner": "backend.source_universe_backend",
        "truth_owner": "backend",
        "cockpit_role": "presentation_only",
        "purpose": "Expose configured governed source universes for evidence-producing discovery contexts.",
        "required_state": "single_owner",
        "compatibility_policy": "universes provide context only; they do not directly promote runtime truth",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def build_registry() -> Dict[str, Any]:
    audit = load_json(V19_84_3_REPORT)
    critical_status = audit.get("critical_route_status", {}) if isinstance(audit, dict) else {}

    routes: Dict[str, Any] = {}
    for route, spec in CANONICAL_ROUTE_OWNERS.items():
        audit_state = critical_status.get(route, {}) if isinstance(critical_status, dict) else {}
        state = audit_state.get("state", "unknown")
        if state == "single_owner":
            action = "keep"
        elif state == "duplicate_owner":
            action = "assign_canonical_and_demote_duplicates"
        elif state == "missing":
            action = "verify_or_restore"
        else:
            action = "verify_live_mount"

        routes[route] = {
            **spec,
            "route": route,
            "audit_state_v19_84_3": state,
            "audit_owner_count_v19_84_3": audit_state.get("owner_count", None),
            "implementation_action": action,
        }

    return {
        "version": "v19.84.4",
        "build": "Canonical Route Owner Registry",
        "generated_at": utc_now(),
        "status": "configured",
        "backend_owns_truth": True,
        "cockpit_owns_presentation_only": True,
        "runtime_mutation": "none",
        "route_registry_policy": {
            "one_owner_per_method_path": True,
            "frontend_truth_generation_allowed": False,
            "compatibility_layers_must_delegate": True,
            "empty_pending_unavailable_states_are_valid": True,
            "operator_review_required_before_promotion": True,
        },
        "critical_route_count": len(CANONICAL_ROUTE_OWNERS),
        "routes": routes,
        "source_audit": str(V19_84_3_REPORT.relative_to(ROOT)) if V19_84_3_REPORT.exists() else None,
        "next_build": "v19.84.5 Duplicate Route Fail Test",
    }


def validate_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if registry.get("backend_owns_truth") is not True:
        errors.append("backend_owns_truth must be true")
    if registry.get("cockpit_owns_presentation_only") is not True:
        errors.append("cockpit_owns_presentation_only must be true")

    routes = registry.get("routes", {})
    for route in CANONICAL_ROUTE_OWNERS:
        if route not in routes:
            errors.append(f"missing critical route owner: {route}")
            continue
        item = routes[route]
        if not item.get("canonical_owner"):
            errors.append(f"missing canonical_owner for {route}")
        if item.get("truth_owner") != "backend":
            errors.append(f"{route} truth_owner must be backend")
        if item.get("required_state") != "single_owner":
            errors.append(f"{route} required_state must be single_owner")
        if item.get("cockpit_role") not in {"presentation_only", "operator_command"}:
            errors.append(f"{route} has invalid cockpit_role: {item.get('cockpit_role')}")

        audit_state = item.get("audit_state_v19_84_3")
        if audit_state in {"duplicate_owner", "missing"}:
            warnings.append(f"{route} requires follow-up action: {audit_state}")

    return {
        "status": "ok" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "critical_route_count": len(routes),
    }


def write_markdown(registry: Dict[str, Any], validation: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Claire v19.84.4 Canonical Route Owner Registry")
    lines.append("")
    lines.append(f"- Generated: `{registry['generated_at']}`")
    lines.append(f"- Status: `{registry['status']}`")
    lines.append(f"- Validation: `{validation['status']}`")
    lines.append(f"- Backend owns truth: `{registry['backend_owns_truth']}`")
    lines.append(f"- Cockpit owns presentation only: `{registry['cockpit_owns_presentation_only']}`")
    lines.append("")
    lines.append("## Critical Route Owners")
    lines.append("")
    lines.append("| Route | Canonical Owner | Cockpit Role | Audit State | Action |")
    lines.append("|---|---|---|---|---|")
    for route, item in registry["routes"].items():
        lines.append(
            f"| `{route}` | `{item['canonical_owner']}` | `{item['cockpit_role']}` | "
            f"`{item['audit_state_v19_84_3']}` | `{item['implementation_action']}` |"
        )
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    if validation["errors"]:
        lines.append("### Errors")
        for error in validation["errors"]:
            lines.append(f"- {error}")
        lines.append("")
    if validation["warnings"]:
        lines.append("### Warnings")
        for warning in validation["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    if not validation["errors"] and not validation["warnings"]:
        lines.append("No validation errors or warnings.")
        lines.append("")
    lines.append("## Next Build")
    lines.append("")
    lines.append("v19.84.5 should add the duplicate route fail test and begin enforcing this registry.")
    return "\n".join(lines) + "\n"


def write_registry() -> Dict[str, Any]:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    registry = build_registry()
    validation = validate_registry(registry)

    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")

    report = {
        "version": "v19.84.4",
        "build": "Canonical Route Owner Registry",
        "generated_at": utc_now(),
        "status": validation["status"],
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "validation": validation,
        "registry": registry,
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(registry, validation), encoding="utf-8")
    return report


def main() -> int:
    report = write_registry()
    print(json.dumps({
        "status": report["status"],
        "version": report["version"],
        "registry_path": report["registry_path"],
        "critical_route_count": report["validation"]["critical_route_count"],
        "warnings": len(report["validation"]["warnings"]),
        "errors": len(report["validation"]["errors"]),
    }, indent=2))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
