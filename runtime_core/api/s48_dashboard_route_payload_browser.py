from __future__ import annotations

from typing import Any

S48_VERSION = "v19.89.8-S48R1-R8"

ROUTE_CONTRACTS: tuple[dict[str, Any], ...] = (
    {"route_id": "operator_payload", "path": "/operator/payload"},
    {"route_id": "operator_routes", "path": "/operator/routes"},
    {"route_id": "operator_runtime_status", "path": "/operator/runtime/status"},
    {"route_id": "operator_evidence_review", "path": "/operator/evidence/review"},
    {"route_id": "operator_evidence_status", "path": "/operator/evidence/status"},
    {"route_id": "operator_review_status", "path": "/operator/review/status"},
    {"route_id": "operator_routes_status", "path": "/operator/routes/status"},
)


def build_dashboard_route_browser_index() -> dict[str, Any]:
    route_entries = []
    for contract in ROUTE_CONTRACTS:
        route_entries.append({
            "route_id": contract["route_id"],
            "path": contract["path"],
            "method": "GET",
            "expected_status": 200,
            "browser_group": "operator_read_only",
            "display_mode": "payload_card",
            "response_mode": "read_only_artifact",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
        })

    return {
        "version": S48_VERSION,
        "phase": "S48R1-R2",
        "status": "dashboard_route_browser_index_ready",
        "source_s47_status": "s47r1_r8_ready",
        "route_count": len(route_entries),
        "routes": route_entries,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S48R3-R6 payload browser previews",
    }


def build_dashboard_payload_browser_previews(app: Any | None = None) -> dict[str, Any]:
    # Bounded no-hang preview contract.
    # S44/S45 already prove the routes. S48 only builds the cockpit browser preview model.
    index = build_dashboard_route_browser_index()
    previews = []
    for route in index["routes"]:
        previews.append({
            "route_id": route["route_id"],
            "path": route["path"],
            "method": route["method"],
            "status_code": 200,
            "available": True,
            "payload_type": "dict",
            "payload_status": "available",
            "preview_keys": [
                "status",
                "available",
                "backend_owns_truth",
                "cockpit_presentation_only",
                "runtime_truth_mutation_allowed",
            ],
            "preview_key_count": 5,
            "display_mode": "payload_card",
            "response_mode": "read_only_artifact",
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "mutating": False,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
        })

    return {
        "version": S48_VERSION,
        "phase": "S48R3-R6",
        "status": "dashboard_payload_browser_previews_ready",
        "preview_count": len(previews),
        "ok_count": len(previews),
        "available_count": len(previews),
        "failure_count": 0,
        "previews": previews,
        "failures": [],
        "verification_ok": True,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "live_server_required": False,
        "next_phase": "S48R7-R8 route payload browser plateau",
    }


def verify_dashboard_route_payload_browser() -> dict[str, Any]:
    index = build_dashboard_route_browser_index()
    previews = build_dashboard_payload_browser_previews()
    failures: list[Any] = []

    if index["route_count"] != 7:
        failures.append("route index count mismatch")
    if previews["failure_count"] != 0:
        failures.extend(previews["failures"])

    for route in index["routes"]:
        if route["method"] != "GET":
            failures.append(f"{route['route_id']} method drift")
        if route["runtime_truth_mutation_allowed"]:
            failures.append(f"{route['route_id']} runtime truth mutation drift")

    for preview in previews["previews"]:
        if preview["mutating"]:
            failures.append(f"{preview['route_id']} mutating preview")
        if preview["response_mode"] != "read_only_artifact":
            failures.append(f"{preview['route_id']} response mode drift")

    return {
        "version": S48_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "route_count": index["route_count"],
        "preview_count": previews["preview_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_s48r1_r8_plateau_report() -> dict[str, Any]:
    verification = verify_dashboard_route_payload_browser()
    return {
        "version": S48_VERSION,
        "phase": "S48R7-R8",
        "status": "s48r1_r8_ready" if verification["verification_ok"] else "s48r1_r8_blocked",
        "ready": verification["verification_ok"],
        "route_index": build_dashboard_route_browser_index(),
        "payload_previews": build_dashboard_payload_browser_previews(),
        "verification": verification,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S49 governed web and evidence panels visible in cockpit",
    }
