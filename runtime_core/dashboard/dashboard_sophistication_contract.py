
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, List

PACK_VERSION = "v19.20-v19.24"

COCKPIT_ZONES = [
    "mission_control",
    "main_result",
    "live_web_evidence",
    "runtime_truth",
    "route_progress",
    "trend_thesis",
    "portfolio",
    "breakthrough",
    "autodesign",
    "design_portal",
    "validation",
    "acquisition",
    "system_health",
]

NO_RESTRUCTURE_RULES = [
    "preserve_existing_launcher",
    "preserve_existing_dashboard_entry",
    "append_or_bind_panels_safely",
    "do_not_delete_dashboard_files",
    "do_not_replace_full_ui_without_explicit_approval",
    "keep_search_bar_visible",
    "keep_provider_probe_advanced_manual",
]

DASHBOARD_CURRENCY_REQUIREMENTS = [
    "current_pack_visible",
    "runtime_state_visible",
    "live_connectivity_visible",
    "pipeline_route_visible",
    "main_result_never_blank",
    "blocked_state_visible",
    "insufficient_data_visible",
]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def build_dashboard_sophistication_contract() -> Dict[str, Any]:
    return {
        "pack_version": PACK_VERSION,
        "status": "dashboard_sophistication_contract_locked",
        "approach": "incremental_cockpit_binding_without_full_restructure",
        "cockpit_zones": COCKPIT_ZONES,
        "no_restructure_rules": NO_RESTRUCTURE_RULES,
        "dashboard_currency_requirements": DASHBOARD_CURRENCY_REQUIREMENTS,
        "search_bar_role": [
            "normal_web_search",
            "governed_research",
            "runtime_search",
            "future_agent_command_surface",
        ],
        "provider_probe_role": "advanced_manual_explicit_enable_only",
        "layout_policy": {
            "full_restructure": False,
            "safe_incremental_panel_binding": True,
            "single_launcher_consistency": True,
            "delete_dashboard_files": False,
        },
        "updated_at": utc_now(),
    }

def build_dashboard_panel_manifest() -> Dict[str, Any]:
    return {
        "pack_version": PACK_VERSION,
        "status": "dashboard_panel_manifest_ready",
        "panels": [
            {
                "zone": zone,
                "required": True,
                "binds_runtime_output": zone in [
                    "main_result",
                    "runtime_truth",
                    "route_progress",
                    "trend_thesis",
                    "portfolio",
                    "breakthrough",
                    "autodesign",
                    "design_portal",
                    "validation",
                    "acquisition",
                    "system_health",
                ],
                "binds_live_web": zone == "live_web_evidence",
            }
            for zone in COCKPIT_ZONES
        ],
        "updated_at": utc_now(),
    }

def validate_dashboard_sophistication_contract(contract: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    policy = contract.get("layout_policy", {})
    if policy.get("full_restructure") is not False:
        errors.append("full restructure must remain false")
    if policy.get("safe_incremental_panel_binding") is not True:
        errors.append("safe incremental panel binding must remain true")
    if policy.get("single_launcher_consistency") is not True:
        errors.append("single launcher consistency required")
    if policy.get("delete_dashboard_files") is not False:
        errors.append("dashboard files must not be deleted")
    for rule in NO_RESTRUCTURE_RULES:
        if rule not in contract.get("no_restructure_rules", []):
            errors.append(f"missing no-restructure rule: {rule}")
    for zone in COCKPIT_ZONES:
        if zone not in contract.get("cockpit_zones", []):
            errors.append(f"missing cockpit zone: {zone}")
    if "keep_search_bar_visible" not in contract.get("no_restructure_rules", []):
        errors.append("search bar must remain visible")
    return errors

def validate_panel_manifest(manifest: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    panels = manifest.get("panels", [])
    zones = [p.get("zone") for p in panels]
    for zone in COCKPIT_ZONES:
        if zone not in zones:
            errors.append(f"missing panel zone: {zone}")
    if not any(p.get("binds_live_web") for p in panels):
        errors.append("at least one panel must bind live web evidence")
    if not any(p.get("binds_runtime_output") and p.get("zone") == "main_result" for p in panels):
        errors.append("main_result must bind runtime output")
    if not any(p.get("binds_runtime_output") and p.get("zone") == "system_health" for p in panels):
        errors.append("system_health must bind runtime output")
    return errors

def build_dashboard_sophistication_report() -> Dict[str, Any]:
    contract = build_dashboard_sophistication_contract()
    panel_manifest = build_dashboard_panel_manifest()
    errors = validate_dashboard_sophistication_contract(contract) + validate_panel_manifest(panel_manifest)
    return {
        "pack_version": PACK_VERSION,
        "pack_name": "Dashboard Sophistication Pass without Full Restructure Pack",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "proofs": {
            "full_restructure_avoided": contract["layout_policy"]["full_restructure"] is False,
            "safe_incremental_binding": contract["layout_policy"]["safe_incremental_panel_binding"] is True,
            "single_launcher_consistency": contract["layout_policy"]["single_launcher_consistency"] is True,
            "search_bar_preserved": "keep_search_bar_visible" in contract["no_restructure_rules"],
            "provider_probe_manual": contract["provider_probe_role"] == "advanced_manual_explicit_enable_only",
            "cockpit_zones_present": len(panel_manifest["panels"]) == len(COCKPIT_ZONES),
        },
        "contract": contract,
        "panel_manifest": panel_manifest,
        "updated_at": utc_now(),
    }
