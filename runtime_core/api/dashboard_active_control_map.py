from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


VERSION = "v19.89.8-S1323-S1350-dashboard-active-control-map"


ACTIVE_CONTROL_MAP: list[dict[str, Any]] = [
    {
        "key": "system_health_plateau",
        "label": "System Health & Plateau Lock",
        "category": "System",
        "description": "Verify health, audit proof, and project plateau lock.",
        "primary_endpoint": "/api/audit/plateau-lock",
        "secondary_endpoints": ["/health", "/dashboard/audit/plateau-lock"],
        "button_label": "Check system plateau",
        "operation_mode": "read_only",
    },
    {
        "key": "dashboard_payload",
        "label": "Dashboard Payload",
        "category": "Dashboard",
        "description": "Load canonical dashboard payload and payload status.",
        "primary_endpoint": "/dashboard/payload",
        "secondary_endpoints": ["/dashboard/payload/status"],
        "button_label": "Refresh payload",
        "operation_mode": "read_only",
    },
    {
        "key": "dashboard_actions",
        "label": "Dashboard Actions",
        "category": "Dashboard",
        "description": "Load action registry, summary, preview, and result surfaces.",
        "primary_endpoint": "/dashboard/actions/registry",
        "secondary_endpoints": ["/dashboard/actions/summary", "/dashboard/actions/preview/plan_search", "/dashboard/actions/result/plan_search"],
        "button_label": "Review action registry",
        "operation_mode": "review_only",
    },
    {
        "key": "operator_console",
        "label": "Operator Console",
        "category": "Operations",
        "description": "Load governed operator console controls and action previews.",
        "primary_endpoint": "/dashboard/operator-console/actions",
        "secondary_endpoints": ["/dashboard/operator-console/contract", "/dashboard/operator-console/summary", "/dashboard/operator-console/preview/plan_search", "/dashboard/operator-action/result/plan_search"],
        "button_label": "Open operator controls",
        "operation_mode": "review_only",
    },
    {
        "key": "cockpit_operations",
        "label": "Cockpit Operations",
        "category": "Operations",
        "description": "Load cockpit operations, control surface, visual operations, and operational proof.",
        "primary_endpoint": "/api/cockpit/operations/payload",
        "secondary_endpoints": ["/api/cockpit/control-surface/payload", "/api/cockpit/operation-visuals/payload", "/api/cockpit/operator-experience/payload", "/api/cockpit/operational-proof"],
        "button_label": "Load cockpit operations",
        "operation_mode": "review_only",
    },
    {
        "key": "command_bar",
        "label": "Command Bar Operations",
        "category": "Command",
        "description": "Load command-bar operation payload, buttons, and preview state.",
        "primary_endpoint": "/api/cockpit/command/latest",
        "secondary_endpoints": ["/api/cockpit/command/history", "/api/cockpit/command/plan"],
        "button_label": "Load command bar controls",
        "operation_mode": "preview_only",
    },
    {
        "key": "governed_search",
        "label": "Governed Search",
        "category": "Search",
        "description": "Load governed search plans, cards, actions, and result quarantine surfaces.",
        "primary_endpoint": "/api/search/governed/query/payload",
        "secondary_endpoints": ["/api/search/governed/query/cards", "/api/search/governed/query/actions", "/api/cockpit/search/consolidated-payload", "/api/evidence/quarantine/status"],
        "button_label": "Review governed search",
        "operation_mode": "review_only",
    },
    {
        "key": "provider_readiness",
        "label": "Provider Readiness",
        "category": "Search",
        "description": "Load provider readiness, configuration, manual probe, and stop-gate surfaces.",
        "primary_endpoint": "/api/search/providers/capability/payload",
        "secondary_endpoints": ["/api/search/providers/capability/status", "/api/search/providers/configuration/payload", "/api/search/provider/manual-probe/preflight", "/api/search/providers/capability/stop-gate"],
        "button_label": "Check providers",
        "operation_mode": "read_only",
    },
    {
        "key": "metadata_live_probe",
        "label": "Metadata / Live Probe Boundary",
        "category": "Internet",
        "description": "Load metadata contract and live-probe status without executing a live probe.",
        "primary_endpoint": "/api/search/metadata/adapter/payload",
        "secondary_endpoints": ["/api/search/metadata/adapter/boundary", "/api/search/metadata/probe/manual/status", "/api/governed/live-probe/status", "/api/cockpit/metadata-search/payload"],
        "button_label": "Review probe boundary",
        "operation_mode": "read_only",
    },
    {
        "key": "evidence_review",
        "label": "Evidence Review",
        "category": "Evidence",
        "description": "Load governed evidence, quarantine, review, and promotion-preview surfaces.",
        "primary_endpoint": "/api/evidence/quarantine/status",
        "secondary_endpoints": ["/api/evidence/source/intake", "/api/evidence/quarantine/review-queue", "/api/evidence/quarantine/actions", "/api/evidence/quarantine/policy"],
        "button_label": "Review evidence",
        "operation_mode": "review_only",
    },
    {
        "key": "source_registry_policy",
        "label": "Source Registry & Policy",
        "category": "Sources",
        "description": "Load source registry, policy, gaps, intake, and live source catalog status.",
        "primary_endpoint": "/api/sources/policy/payload",
        "secondary_endpoints": ["/api/sources/policy/status", "/api/sources/policy/controls", "/api/evidence/source/intake"],
        "button_label": "Review sources",
        "operation_mode": "read_only",
    },
    {
        "key": "body_read_gates",
        "label": "Body-Read Gates",
        "category": "Governance",
        "description": "Load body-read authorization, sanitizer, manual gate, and stop-gate state without body reads.",
        "primary_endpoint": "/api/cockpit/body-read-gate/status",
        "secondary_endpoints": ["/api/web/body-read/authorization/payload", "/api/cockpit/body-read-gate/payload", "/api/cockpit/body-read-gate/stop-gate"],
        "button_label": "Review body-read gate",
        "operation_mode": "blocked_review_only",
    },
    {
        "key": "runtime_spine_lifecycle",
        "label": "Runtime Spine & Lifecycle",
        "category": "Runtime",
        "description": "Load runtime spine, authority map, evidence bridge, and lifecycle routing preview.",
        "primary_endpoint": "/runtime/status",
        "secondary_endpoints": ["/runtime/state", "/runtime/continuous/status", "/dashboard/runtime-truth"],
        "button_label": "Review runtime spine",
        "operation_mode": "read_only",
    },
    {
        "key": "update_truth_promotion",
        "label": "Update & Runtime Truth Preview",
        "category": "Governance",
        "description": "Load update proposal, install readiness, source ingestion draft, and runtime truth promotion preview.",
        "primary_endpoint": "/api/update-governance/open-web/panel",
        "secondary_endpoints": [
            "/api/platform/update/plan",
            "/api/update-governance/open-web/readiness",
            "/api/update-governance/open-web/install/status/live_portfolio_proof_update_probe",
            "/dashboard/update-governance/panel",
        ],
        "button_label": "Review update proposal",
        "operation_mode": "operator_gated_install_ready",
    },
    {
        "key": "endpoint_standard_package",
        "label": "Endpoint Standards Package",
        "category": "Governance",
        "description": "Load the industry-standard endpoint expectation package and settings proof.",
        "primary_endpoint": "/api/system/industry-standard-endpoint-package",
        "secondary_endpoints": ["/api/system/endpoint-standard-settings", "/dashboard/system/industry-standard-endpoint-package", "/openapi.json"],
        "button_label": "Review endpoint package",
        "operation_mode": "read_only_proof_package",
    },
    {
        "key": "endpoint_reconciliation",
        "label": "Endpoint Reconciliation",
        "category": "Governance",
        "description": "Load active frontend/backend endpoint reconciliation and compatibility alias status.",
        "primary_endpoint": "/api/system/endpoint-reconciliation",
        "secondary_endpoints": ["/dashboard/system/endpoint-reconciliation", "/api/system/industry-standard-endpoint-package"],
        "button_label": "Review endpoint reconciliation",
        "operation_mode": "read_only_proof_package",
    },
    {
        "key": "dependency_chain_proof",
        "label": "Dependency Chain Proof",
        "category": "Governance",
        "description": "Run the current dependency-to-dependency end-to-end proof chain.",
        "primary_endpoint": "/api/system/dependency-chain-proof",
        "secondary_endpoints": ["/proof/dependency-chain", "/api/system/endpoint-reconciliation", "/api/system/industry-standard-endpoint-package"],
        "button_label": "Run dependency proof",
        "operation_mode": "read_only_e2e_proof",
    },
    {
        "key": "design_cad_contract",
        "label": "Design / CAD Contract",
        "category": "Design",
        "description": "Load Design Portal status, output contract, and CAD intent without exposing CAD export.",
        "primary_endpoint": "/design-portal/status",
        "secondary_endpoints": ["/design-portal/contract", "/design-portal/output", "/cad/intent"],
        "button_label": "Review Design/CAD contract",
        "operation_mode": "contract_review_only",
    },
    {
        "key": "live_intelligence_catalog",
        "label": "Live Intelligence & Catalog",
        "category": "Internet",
        "description": "Load live intelligence status and live source catalog health.",
        "primary_endpoint": "/runtime/continuous/status",
        "secondary_endpoints": ["/runtime/continuous/cycles", "/runtime/continuous/review-queue"],
        "button_label": "Check live intelligence",
        "operation_mode": "read_only",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_authority() -> dict[str, str]:
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


def _control_with_authority(control: dict[str, Any]) -> dict[str, Any]:
    payload = dict(control)
    payload.update(
        {
            "enabled": True,
            "visible": True,
            "safe_to_click": True,
            "execution_enabled": False,
            "network_request_authority": False,
            "body_read_allowed": False,
            "runtime_mutation_allowed": False,
            "runtime_truth_mutation_allowed": False,
            "package_install_allowed": False,
            "command_execution_allowed": False,
            "result_target": "claire-active-control-result-pane",
        }
    )
    return payload


def build_dashboard_active_control_map() -> dict[str, Any]:
    controls = [_control_with_authority(control) for control in ACTIVE_CONTROL_MAP]
    return {
        "ok": True,
        "status": "ready",
        "version": VERSION,
        "generated_at": _utc_now(),
        "control_count": len(controls),
        "bound_from_audit": "S1295-S1322",
        "purpose": "Expose visible dashboard controls for each required backend capability found by the system-vs-dashboard gap audit.",
        "controls": controls,
        "categories": sorted({control["category"] for control in controls}),
        "frontend_contract": {
            "must_render_visible_buttons": True,
            "must_fetch_this_map": "/api/dashboard/active-control-map",
            "must_fetch_control_primary_endpoint_on_click": True,
            "must_render_result_pane": True,
            "must_show_blocked_authority": True,
        },
        "authority": {
            "all_controls_review_or_read_only": True,
            "unsafe_authority_unlocked": False,
            "blocked": _blocked_authority(),
        },
    }
