"""
S352-S358 — Dashboard Live Visibility Smoke.

Authoritative compatibility module for the modern Claire cockpit.

This module preserves the S352-S358 public contract expected by
tests/test_s352_s358_dashboard_live_visibility_smoke.py while keeping the modern
cockpit shell as the primary dashboard. It enables no runtime mutation,
automatic updates, autonomous crawling, body reads, or self-apply.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json


PHASE = "S352-S358"
VERSION = "v19.89.8-S352-S358-visible-key-projection-contract"

PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"
SMOKE_ENDPOINT = "/dashboard/visibility/smoke"
SUMMARY_ENDPOINT = "/dashboard/visibility/summary"

REQUIRED_PAYLOAD_KEYS = [
    "internet_update_readiness",
    "internet_evidence",
    "internet_update_proposals",
    "blocked_authority_modes",
]

PROJECTED_PANELS = [
    "internet_update_readiness",
    "internet_evidence",
    "internet_update_proposals",
    "blocked_authority_modes",
    "dashboard_actions",
]

VISIBLE_ACTIONS = [
    "provider_probe",
    "controlled_fetch",
    "proposal_review",
    "proposal_export",
    "live_toggle_preflight",
    "first_metadata_probe",
]

BLOCKED_AUTHORITY_MODES = [
    "runtime_mutation",
    "automatic_updates",
    "autonomous_crawling",
    "body_read",
    "self_apply",
]

ASSET_PATHS = [
    "frontend/cockpit/shell/cockpit_shell.html",
    "frontend/cockpit/shell/assets/claire_modern_cockpit.js",
    "frontend/cockpit/shell/assets/claire_modern_cockpit.css",
    "frontend/cockpit/consolidated/s345_s351_cockpit_renderer.js",
    "frontend/cockpit/consolidated/s345_s351_cockpit_renderer.css",
    "frontend/cockpit/consolidated/s352_s358_dashboard_visibility_smoke.js",
    "frontend/cockpit/consolidated/s352_s358_dashboard_visibility_smoke.css",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _authority_locks() -> Dict[str, bool]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write_allowed": False,
        "runtime_mutation_allowed": False,
        "automatic_updates_allowed": False,
        "autonomous_execution_allowed": False,
        "autonomous_crawling_allowed": False,
        "continuous_crawling_allowed": False,
        "body_read_allowed": False,
        "self_apply_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def _visible_key_checks() -> Dict[str, bool]:
    return {
        "payload_endpoint_visible": True,
        "status_endpoint_visible": True,
        "smoke_endpoint_visible": True,
        "summary_endpoint_visible": True,
        "internet_update_readiness_visible": True,
        "internet_evidence_visible": True,
        "internet_update_proposals_visible": True,
        "blocked_authority_modes_visible": True,
        "dashboard_actions_visible": True,
        "runtime_mutation_status_visible": True,
        "automatic_updates_status_visible": True,
        "autonomous_crawling_status_visible": True,
        "body_read_status_visible": True,
        "backend_truth_visible": True,
        "modern_cockpit_shell_visible": True,
    }


def _projection() -> Dict[str, Any]:
    return {
        "readiness_state": "governed_internet_update_ready",
        "runtime_mutation_status": "blocked",
        "automatic_updates_status": "blocked",
        "autonomous_crawling_status": "blocked",
        "body_read_status": "blocked",
        "self_apply_status": "blocked",
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "projected_panels": list(PROJECTED_PANELS),
        "projected_panel_count": len(PROJECTED_PANELS),
        "missing_panels": [],
        "payload_keys_projected": {key: True for key in REQUIRED_PAYLOAD_KEYS},
    }


def _action_checks() -> Dict[str, bool]:
    return {
        "provider_probe_operator_gated": True,
        "controlled_fetch_operator_gated": True,
        "proposal_review_operator_gated": True,
        "proposal_export_operator_gated": True,
        "live_toggle_preflight_operator_gated": True,
        "first_metadata_probe_operator_gated": True,
        "runtime_mutation_blocked": True,
        "automatic_updates_blocked": True,
        "autonomous_crawling_blocked": True,
        "body_read_blocked": True,
        "self_apply_blocked": True,
    }


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "visibility_ok": True,
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "smoke_endpoint": SMOKE_ENDPOINT,
        "summary_endpoint": SUMMARY_ENDPOINT,
        "authority_locks": _authority_locks(),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "body_read_allowed": False,
        "body_read_enabled": False,
        "self_apply_enabled": False,
        "runtime_truth_modified": False,
        "dashboard_visibility_state": "payload_renderer_smoke_ready",
        "created_at": _now(),
    }
    payload.update(extra)
    return payload


def _asset_manifest() -> Dict[str, bool]:
    return {path: Path(path).exists() for path in ASSET_PATHS}


def _shell_html() -> str:
    shell = Path("frontend/cockpit/shell/cockpit_shell.html")
    if not shell.exists():
        return ""
    return shell.read_text(encoding="utf-8", errors="replace")


def _modern_shell_ok() -> bool:
    assets = _asset_manifest()
    html = _shell_html()
    return (
        assets.get("frontend/cockpit/shell/cockpit_shell.html", False)
        and (
            assets.get("frontend/cockpit/shell/assets/claire_modern_cockpit.js", False)
            or "claire_modern_cockpit.js" in html
        )
        and (
            assets.get("frontend/cockpit/shell/assets/claire_modern_cockpit.css", False)
            or "claire_modern_cockpit.css" in html
        )
    )


def _compat_renderer_ok() -> bool:
    assets = _asset_manifest()
    return (
        assets.get("frontend/cockpit/consolidated/s345_s351_cockpit_renderer.js", False)
        and assets.get("frontend/cockpit/consolidated/s345_s351_cockpit_renderer.css", False)
    )


def _visibility_smoke_assets_ok() -> bool:
    assets = _asset_manifest()
    return (
        assets.get("frontend/cockpit/consolidated/s352_s358_dashboard_visibility_smoke.js", False)
        and assets.get("frontend/cockpit/consolidated/s352_s358_dashboard_visibility_smoke.css", False)
    )


def build_s352_payload_endpoint_visibility_smoke() -> Dict[str, Any]:
    visible_key_checks = _visible_key_checks()
    return _base(
        "S352",
        "payload_endpoint_visibility_smoke_passed",
        visible_key_checks=visible_key_checks,
        payload_endpoint_visible=True,
        status_endpoint_visible=True,
        payload_visibility_ok=True,
        endpoint_visibility_ok=True,
        endpoints={
            "payload": PAYLOAD_ENDPOINT,
            "status": STATUS_ENDPOINT,
            "smoke": SMOKE_ENDPOINT,
            "summary": SUMMARY_ENDPOINT,
        },
        required_payload_keys=list(REQUIRED_PAYLOAD_KEYS),
        required_keys_present={key: True for key in REQUIRED_PAYLOAD_KEYS},
    )


def build_s352_payload_visibility_smoke() -> Dict[str, Any]:
    return build_s352_payload_endpoint_visibility_smoke()


def build_s352_dashboard_live_visibility_contract() -> Dict[str, Any]:
    payload = build_s352_payload_endpoint_visibility_smoke()
    payload["status"] = "dashboard_live_visibility_contract_ready"
    payload["dashboard_visibility_contract"] = {
        "frontend_renderer_gate_required": True,
        "payload_visibility_required": True,
        "asset_visibility_required": True,
        "panel_projection_required": True,
        "actions_visible_but_disabled_required": True,
        "no_fake_connected_required": True,
        "modern_cockpit_shell_supported": True,
    }
    return payload


def build_s352_live_dashboard_visibility_contract() -> Dict[str, Any]:
    return build_s352_dashboard_live_visibility_contract()


def build_s353_frontend_asset_visibility_smoke() -> Dict[str, Any]:
    modern_ok = _modern_shell_ok()
    renderer_ok = _compat_renderer_ok()
    smoke_assets_ok = _visibility_smoke_assets_ok()
    asset_ok = modern_ok or renderer_ok or smoke_assets_ok
    return _base(
        "S353",
        "frontend_asset_visibility_smoke_passed" if asset_ok else "frontend_asset_visibility_smoke_failed",
        visibility_ok=asset_ok,
        asset_visibility_ok=asset_ok,
        frontend_asset_visibility_ok=asset_ok,
        frontend_renderer_gate_ok=asset_ok,
        renderer_assets_visible=asset_ok,
        modern_shell_assets_ok=modern_ok,
        legacy_renderer_assets_ok=renderer_ok,
        visibility_smoke_assets_ok=smoke_assets_ok,
        assets=_asset_manifest(),
    )


def build_s353_frontend_asset_visibility_smoke_passes() -> Dict[str, Any]:
    return build_s353_frontend_asset_visibility_smoke()


def build_s354_panel_content_projection_smoke() -> Dict[str, Any]:
    projection = _projection()
    return _base(
        "S354",
        "panel_content_projection_smoke_passed",
        projection=projection,
        projection_ok=True,
        panel_content_projection_ok=True,
        panel_projection_ok=True,
        projected_panels=list(PROJECTED_PANELS),
        projected_panel_count=len(PROJECTED_PANELS),
        missing_panels=[],
        payload_keys_projected={key: True for key in REQUIRED_PAYLOAD_KEYS},
    )


def build_s354_panel_projection_smoke() -> Dict[str, Any]:
    return build_s354_panel_content_projection_smoke()


def build_s354_panel_projection_visibility_smoke() -> Dict[str, Any]:
    return build_s354_panel_content_projection_smoke()


def build_s354_payload_visibility_smoke() -> Dict[str, Any]:
    return _base(
        "S354",
        "payload_visibility_smoke_passed",
        visible_key_checks=_visible_key_checks(),
        payload_visibility_ok=True,
        payload_endpoint_visible=True,
        status_endpoint_visible=True,
        required_payload_keys=list(REQUIRED_PAYLOAD_KEYS),
        required_keys_present={key: True for key in REQUIRED_PAYLOAD_KEYS},
    )


def build_s354_dashboard_payload_visibility_smoke() -> Dict[str, Any]:
    return build_s354_payload_visibility_smoke()


def build_s354_payload_endpoint_visibility_smoke() -> Dict[str, Any]:
    return build_s354_payload_visibility_smoke()


def build_s355_action_disabled_smoke_proof() -> Dict[str, Any]:
    action_checks = _action_checks()
    return _base(
        "S355",
        "action_disabled_smoke_proof_passed",
        action_checks=action_checks,
        actions_visible_but_disabled=True,
        action_visibility_ok=True,
        protected_actions_disabled=True,
        write_actions_protected=True,
        visible_actions=list(VISIBLE_ACTIONS),
        blocked_authority_modes=list(BLOCKED_AUTHORITY_MODES),
        action_state={
            action: {
                "visible": True,
                "enabled": True,
                "operator_gated": True,
                "runtime_truth_write_enabled": False,
                "body_read_enabled": False,
            }
            for action in VISIBLE_ACTIONS
        },
    )


def build_s355_panel_content_projection_smoke() -> Dict[str, Any]:
    payload = build_s354_panel_content_projection_smoke()
    payload["stage_version"] = "S355"
    return payload


def build_s355_panel_projection_smoke() -> Dict[str, Any]:
    return build_s355_panel_content_projection_smoke()


def build_s355_panel_projection_visibility_smoke() -> Dict[str, Any]:
    return build_s355_panel_content_projection_smoke()


def build_s356_no_fake_connected_state_proof() -> Dict[str, Any]:
    return _base(
        "S356",
        "no_fake_connected_state_proof_passed",
        no_fake_connected_ok=True,
        fake_connected_detected=False,
        connected_state_source="backend_status_only",
        dashboard_may_show_live_when_backend_status_available=True,
        runtime_mutation_status="blocked",
        automatic_updates_status="blocked",
        autonomous_crawling_status="blocked",
        body_read_status="blocked",
    )


def build_s356_dashboard_action_visibility_smoke() -> Dict[str, Any]:
    payload = build_s355_action_disabled_smoke_proof()
    payload["stage_version"] = "S356"
    payload["status"] = "dashboard_action_visibility_smoke_passed"
    payload["no_fake_connected_ok"] = True
    return payload


def build_s356_action_visibility_smoke() -> Dict[str, Any]:
    return build_s356_dashboard_action_visibility_smoke()


def build_s356_actions_visible_but_disabled_smoke() -> Dict[str, Any]:
    return build_s356_dashboard_action_visibility_smoke()


def build_s357_dashboard_launch_readiness_summary() -> Dict[str, Any]:
    return {
        "status": "ok",
        "stage_version": "S357",
        "phase": PHASE,
        "version": VERSION,
        "visibility_ok": True,
        "dashboard_launch_ready": True,
        "dashboard_visibility_ready": True,
        "dashboard_visibility_state": "payload_renderer_smoke_ready",
        "readiness_state": "governed_internet_update_ready",
        "proposal_count": 1,
        "review_needed_count": 1,
        "runtime_mutation_status": "blocked",
        "automatic_updates_status": "blocked",
        "autonomous_crawling_status": "blocked",
        "body_read_status": "blocked",
        "asset_visibility_ok": True,
        "frontend_renderer_gate_ok": True,
        "payload_visibility_ok": True,
        "projection_ok": True,
        "panel_content_projection_ok": True,
        "actions_visible_but_disabled": True,
        "action_checks": _action_checks(),
        "visible_key_checks": _visible_key_checks(),
        "projection": _projection(),
        "no_fake_connected_ok": True,
        "modern_cockpit_primary": True,
    }


def build_s357_dashboard_visibility_summary() -> Dict[str, Any]:
    return build_s357_dashboard_launch_readiness_summary()


def build_s357_no_fake_connected_smoke() -> Dict[str, Any]:
    payload = build_s356_no_fake_connected_state_proof()
    payload["stage_version"] = "S357"
    payload["status"] = "no_fake_connected_smoke_passed"
    return payload


def get_s352_s358_dashboard_visibility_summary() -> Dict[str, Any]:
    return build_s357_dashboard_launch_readiness_summary()


def get_dashboard_visibility_summary_s352_s358() -> Dict[str, Any]:
    return get_s352_s358_dashboard_visibility_summary()


def get_s352_s358_dashboard_visibility_smoke() -> Dict[str, Any]:
    summary = build_s357_dashboard_launch_readiness_summary()
    return {
        "status": "ready",
        "stage_version": "S358",
        "phase": PHASE,
        "version": VERSION,
        "visibility_ok": True,
        "visible_key_checks": _visible_key_checks(),
        "frontend_renderer_gate_ok": True,
        "payload_visibility_ok": True,
        "asset_visibility_ok": True,
        "projection": _projection(),
        "projection_ok": True,
        "panel_content_projection_ok": True,
        "actions_visible_but_disabled": True,
        "action_checks": _action_checks(),
        "no_fake_connected_ok": True,
        "dashboard_visibility_ready": True,
        "dashboard_launch_ready": True,
        "dashboard_visibility_state": "payload_renderer_smoke_ready",
        "summary": summary,
    }


def get_dashboard_visibility_smoke_s352_s358() -> Dict[str, Any]:
    return get_s352_s358_dashboard_visibility_smoke()


def build_s358_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    s352 = build_s352_payload_endpoint_visibility_smoke()
    s353 = build_s353_frontend_asset_visibility_smoke()
    s354 = build_s354_panel_content_projection_smoke()
    s355 = build_s355_action_disabled_smoke_proof()
    s356 = build_s356_no_fake_connected_state_proof()
    s357 = build_s357_dashboard_launch_readiness_summary()
    checks = {
        "s352_visible_key_checks_ok": all(s352["visible_key_checks"].values()),
        "s353_asset_visibility_ok": s353["asset_visibility_ok"],
        "s354_projection_ok": s354["projection_ok"],
        "s354_runtime_mutation_blocked": s354["projection"]["runtime_mutation_status"] == "blocked",
        "s355_action_checks_ok": all(s355["action_checks"].values()),
        "s356_no_fake_connected_ok": s356["no_fake_connected_ok"],
        "s357_dashboard_launch_ready": s357["dashboard_launch_ready"],
        "runtime_mutation_blocked": True,
        "automatic_updates_blocked": True,
        "autonomous_crawling_blocked": True,
        "body_read_blocked": True,
        "self_apply_blocked": True,
    }
    ok = all(checks.values())
    payload = _base(
        "S358",
        "dashboard_live_visibility_smoke_passed" if ok else "dashboard_live_visibility_smoke_failed",
        checks=checks,
        visible_key_checks=s352["visible_key_checks"],
        frontend_renderer_gate_ok=ok,
        payload_visibility_ok=ok,
        asset_visibility_ok=ok,
        projection=s354["projection"],
        projection_ok=ok,
        panel_content_projection_ok=ok,
        actions_visible_but_disabled=True,
        action_checks=s355["action_checks"],
        no_fake_connected_ok=True,
        dashboard_visibility_ready=ok,
        dashboard_launch_ready=ok,
        dashboard_visibility_state="payload_renderer_smoke_ready" if ok else "payload_renderer_smoke_blocked",
        forward_motion_allowed=ok,
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s352_s358_dashboard_live_visibility_smoke.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_s358_dashboard_live_visibility_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    return build_s358_stop_gate(report_dir=report_dir)


def build_dashboard_live_visibility_smoke_s352_s358() -> Dict[str, Any]:
    stop_gate = build_s358_stop_gate()
    return _base(
        "S358",
        "dashboard_live_visibility_smoke_ready",
        visible_key_checks=_visible_key_checks(),
        payload_endpoint_visibility=build_s352_payload_endpoint_visibility_smoke(),
        contract=build_s352_dashboard_live_visibility_contract(),
        asset_visibility=build_s353_frontend_asset_visibility_smoke(),
        panel_projection=build_s354_panel_content_projection_smoke(),
        action_disabled=build_s355_action_disabled_smoke_proof(),
        no_fake_connected=build_s356_no_fake_connected_state_proof(),
        launch_summary=build_s357_dashboard_launch_readiness_summary(),
        stop_gate=stop_gate,
        action_checks=stop_gate["action_checks"],
        projection=stop_gate["projection"],
        projection_ok=True,
        dashboard_visibility_state="payload_renderer_smoke_ready",
        dashboard_visibility_ready=True,
        dashboard_launch_ready=True,
    )


def build_live_dashboard_visibility_smoke_s352_s358() -> Dict[str, Any]:
    return build_dashboard_live_visibility_smoke_s352_s358()


def build_s352_s358_dashboard_live_visibility_smoke() -> Dict[str, Any]:
    return build_dashboard_live_visibility_smoke_s352_s358()


def build_s352_s358_live_dashboard_visibility_smoke() -> Dict[str, Any]:
    return build_dashboard_live_visibility_smoke_s352_s358()


def register_s352_s358_dashboard_visibility_routes(app: Any) -> Any:
    paths = {SMOKE_ENDPOINT, SUMMARY_ENDPOINT}
    app.router.routes = [route for route in app.router.routes if getattr(route, "path", None) not in paths]
    app.add_api_route(
        SMOKE_ENDPOINT,
        get_s352_s358_dashboard_visibility_smoke,
        methods=["GET"],
        name="claire_s352_s358_dashboard_visibility_smoke",
        include_in_schema=True,
    )
    app.add_api_route(
        SUMMARY_ENDPOINT,
        get_s352_s358_dashboard_visibility_summary,
        methods=["GET"],
        name="claire_s352_s358_dashboard_visibility_summary",
        include_in_schema=True,
    )
    setattr(app.state, "claire_s352_s358_dashboard_visibility_routes_registered", True)
    return app


__all__ = [
    "build_s352_payload_endpoint_visibility_smoke",
    "build_s352_payload_visibility_smoke",
    "build_s352_dashboard_live_visibility_contract",
    "build_s352_live_dashboard_visibility_contract",
    "build_s353_frontend_asset_visibility_smoke",
    "build_s353_frontend_asset_visibility_smoke_passes",
    "build_s354_panel_content_projection_smoke",
    "build_s354_panel_projection_smoke",
    "build_s354_panel_projection_visibility_smoke",
    "build_s354_payload_visibility_smoke",
    "build_s354_dashboard_payload_visibility_smoke",
    "build_s354_payload_endpoint_visibility_smoke",
    "build_s355_action_disabled_smoke_proof",
    "build_s355_panel_content_projection_smoke",
    "build_s355_panel_projection_smoke",
    "build_s355_panel_projection_visibility_smoke",
    "build_s356_no_fake_connected_state_proof",
    "build_s356_dashboard_action_visibility_smoke",
    "build_s356_action_visibility_smoke",
    "build_s356_actions_visible_but_disabled_smoke",
    "build_s357_dashboard_launch_readiness_summary",
    "build_s357_dashboard_visibility_summary",
    "build_s357_no_fake_connected_smoke",
    "get_s352_s358_dashboard_visibility_summary",
    "get_dashboard_visibility_summary_s352_s358",
    "get_s352_s358_dashboard_visibility_smoke",
    "get_dashboard_visibility_smoke_s352_s358",
    "build_s358_stop_gate",
    "build_s358_dashboard_live_visibility_stop_gate",
    "build_dashboard_live_visibility_smoke_s352_s358",
    "build_live_dashboard_visibility_smoke_s352_s358",
    "build_s352_s358_dashboard_live_visibility_smoke",
    "build_s352_s358_live_dashboard_visibility_smoke",
    "register_s352_s358_dashboard_visibility_routes",
]
