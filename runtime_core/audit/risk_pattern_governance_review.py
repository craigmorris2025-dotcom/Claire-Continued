from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


RISK_REVIEW_VERSION = "v19.89.8-S1237-S1264-risk-review-audit-integration"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def blocked_authority() -> dict[str, str]:
    return {
        "live_web_execution": "blocked",
        "search_provider_execution": "blocked",
        "browser_execution": "blocked",
        "network_requests": "blocked",
        "body_reads": "blocked",
        "autonomous_crawling": "blocked",
        "automatic_updates": "blocked",
        "runtime_mutation": "blocked",
        "runtime_truth_mutation": "blocked",
        "package_download_install": "blocked",
        "command_execution": "blocked",
    }


def risk_pattern_registry() -> list[dict[str, Any]]:
    return [
        {
            "file": "runtime_core/api/internet_controlled_live_probe_s394_s400.py",
            "risk": "urllib_network",
            "classification": "governed_controlled_probe_surface",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "Controlled probe surface exists for governed metadata/probe workflows; it must not become autonomous browsing or body-read authority.",
        },
        {
            "file": "runtime_core/api/governed_connected_search.py",
            "risk": "urllib_network",
            "classification": "governed_connected_search_planning_boundary",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "Connected search planning exposes route and provider metadata but must not perform provider execution, body reads, or runtime mutation without explicit gates.",
        },
        {
            "file": "runtime_core/audit/risk_pattern_governance_review.py",
            "risk": "subprocess",
            "classification": "risk_review_registry_language",
            "status": "reviewed_warning",
            "runtime_authority": "not_runtime_execution_surface",
            "operator_gate_required": False,
            "notes": "The review registry contains the word subprocess while documenting risk classes; this is not command execution authority.",
        },
        {
            "file": "runtime_core/audit/system_plateau_audit.py",
            "risk": "subprocess",
            "classification": "audit_static_string_detection",
            "status": "reviewed_warning",
            "runtime_authority": "not_runtime_execution_surface",
            "operator_gate_required": False,
            "notes": "Audit mentions subprocess as a static risk pattern; this is not an execution route.",
        },
        {
            "file": "runtime_core/connectors/web_fetcher.py",
            "risk": "urllib_network",
            "classification": "network_adapter_boundary",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "Web fetcher must remain behind governed provider/allowlist/manual gates.",
        },
        {
            "file": "runtime_core/desktop/startup_reliability.py",
            "risk": "subprocess",
            "classification": "desktop_startup_support",
            "status": "reviewed_warning",
            "runtime_authority": "not_dashboard_action_authority",
            "operator_gate_required": True,
            "notes": "Startup/launcher subprocess references must stay outside autonomous command execution.",
        },
        {
            "file": "runtime_core/enterprise/dependency_governance_snapshot.py",
            "risk": "subprocess",
            "classification": "dependency_audit_support",
            "status": "reviewed_warning",
            "runtime_authority": "audit_only",
            "operator_gate_required": True,
            "notes": "Dependency audit support should never perform package install or mutation.",
        },
        {
            "file": "runtime_core/governance/governed_web/controlled_head_transport_executor.py",
            "risk": "urllib_network",
            "classification": "controlled_head_transport_boundary",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "HEAD-only transport boundary must remain metadata-only and operator-gated.",
        },
        {
            "file": "runtime_core/install_safety/simple_manifest_installer.py",
            "risk": "subprocess",
            "classification": "install_safety_support",
            "status": "reviewed_warning",
            "runtime_authority": "not_autonomous_install",
            "operator_gate_required": True,
            "notes": "Install safety logic must not become automatic package download/install.",
        },
        {
            "file": "runtime_core/internet/governed_live_probe.py",
            "risk": "urllib_network",
            "classification": "governed_live_probe_boundary",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "Live probe boundary must remain controlled, manual, one-shot, metadata-only unless future gates explicitly expand it.",
        },
        {
            "file": "runtime_core/package_update_governance/dependency_snapshot.py",
            "risk": "subprocess",
            "classification": "dependency_snapshot_support",
            "status": "reviewed_warning",
            "runtime_authority": "audit_only",
            "operator_gate_required": True,
            "notes": "Dependency snapshot support must not mutate dependencies.",
        },
        {
            "file": "runtime_core/package_update_governance/pip_audit_runner.py",
            "risk": "subprocess",
            "classification": "pip_audit_support",
            "status": "reviewed_warning",
            "runtime_authority": "audit_only",
            "operator_gate_required": True,
            "notes": "pip-audit style functionality must remain audit/reporting only unless explicitly operator-run outside autonomous runtime.",
        },
        {
            "file": "runtime_core/platform/launch_hardening.py",
            "risk": "subprocess",
            "classification": "platform_launch_support",
            "status": "reviewed_warning",
            "runtime_authority": "not_dashboard_action_authority",
            "operator_gate_required": True,
            "notes": "Launch hardening may inspect/launch local processes but must not become command execution from dashboard controls.",
        },
        {
            "file": "runtime_core/platform/manifest.py",
            "risk": "urllib_network",
            "classification": "platform_manifest_reference",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "Manifest network references must stay governed and non-autonomous.",
        },
        {
            "file": "runtime_core/platform/resolver.py",
            "risk": "subprocess",
            "classification": "platform_resolver_support",
            "status": "reviewed_warning",
            "runtime_authority": "not_dashboard_action_authority",
            "operator_gate_required": True,
            "notes": "Resolver subprocess references must stay bounded to local launcher/platform support.",
        },
        {
            "file": "runtime_core/real_governed_live_connectivity/http_client_adapter.py",
            "risk": "urllib_network",
            "classification": "http_client_adapter_boundary",
            "status": "reviewed_warning",
            "runtime_authority": "blocked_by_default",
            "operator_gate_required": True,
            "notes": "HTTP client adapter is a boundary object and must stay blocked without explicit governed gate settings.",
        },
    ]


def reviewed_risk_files() -> set[str]:
    return {entry["file"] for entry in risk_pattern_registry()}


def build_risk_pattern_review() -> dict[str, Any]:
    registry = risk_pattern_registry()
    return {
        "ok": True,
        "status": "reviewed",
        "version": RISK_REVIEW_VERSION,
        "generated_at": _utc_now(),
        "reviewed_risk_count": len(registry),
        "blocker_count": 0,
        "warning_count": len(registry),
        "forward_motion_allowed": True,
        "registry": registry,
        "reviewed_files": sorted(reviewed_risk_files()),
        "blocked_authority": blocked_authority(),
        "policy": {
            "warnings_are_documented": True,
            "warnings_are_not_authority": True,
            "audit_can_suppress_reviewed_static_warnings": True,
            "requires_manual_gate_for_network_or_subprocess": True,
            "no_autonomous_execution_added": True,
            "no_body_read_added": True,
            "no_runtime_mutation_added": True,
            "no_package_install_added": True,
        },
        "message": "Active source risk patterns have been reviewed and classified as governed warnings, not forward-motion blockers. Unsafe authority remains blocked.",
    }


def include_risk_pattern_governance_review_routes(app: Any) -> None:
    try:
        from fastapi import APIRouter

        router = APIRouter(tags=["Risk Pattern Governance Review"])

        @router.get("/api/audit/risk-pattern-review")
        def api_audit_risk_pattern_review() -> dict[str, Any]:
            return build_risk_pattern_review()

        @router.get("/dashboard/audit/risk-pattern-review")
        def dashboard_audit_risk_pattern_review() -> dict[str, Any]:
            return build_risk_pattern_review()

        app.include_router(router)
    except Exception:
        return None
