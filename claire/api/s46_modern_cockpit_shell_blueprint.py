from __future__ import annotations

from typing import Any

from claire.api.s46_modern_cockpit_layout_contract import (
    build_modern_cockpit_layout_contract,
    verify_modern_cockpit_layout_contract,
)
from claire.api.s45_panel_data_mounting import build_s45r9_r16_plateau_report


S46_R5_R12_VERSION = "v19.89.8-S46R5-R12"
MODERN_SHELL_ROOT = "frontend/cockpit/modern_shell"
MODERN_SHELL_HTML = f"{MODERN_SHELL_ROOT}/claire_modern_cockpit_shell.html"
MODERN_SHELL_JS = f"{MODERN_SHELL_ROOT}/claire_modern_cockpit_shell.js"
MODERN_SHELL_CSS = f"{MODERN_SHELL_ROOT}/claire_modern_cockpit_shell.css"


def build_modern_cockpit_shell_blueprint() -> dict[str, Any]:
    layout = build_modern_cockpit_layout_contract()
    plateau = build_s45r9_r16_plateau_report()

    shell_regions = []
    for zone in layout["zones"]:
        shell_regions.append({
            "region_id": f"modern-{zone['zone_id']}",
            "zone_id": zone["zone_id"],
            "title": zone["title"],
            "purpose": zone["purpose"],
            "data_source": zone["data_source"],
            "visible": True,
            "render_order": len(shell_regions) + 1,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "automatic_updates_enabled": False,
            "autonomous_execution_enabled": False,
            "response_mode": "read_only_artifact",
        })

    return {
        "version": S46_R5_R12_VERSION,
        "phase": "S46R5-R8",
        "status": "modern_cockpit_shell_blueprint_ready",
        "source_layout_status": layout["status"],
        "source_panel_plateau_status": plateau["status"],
        "asset_root": MODERN_SHELL_ROOT,
        "shell_html": MODERN_SHELL_HTML,
        "shell_js": MODERN_SHELL_JS,
        "shell_css": MODERN_SHELL_CSS,
        "region_count": len(shell_regions),
        "shell_regions": shell_regions,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "next_phase": "S46R9-R12 modern cockpit visible shell asset proof",
    }


def verify_modern_cockpit_shell_blueprint() -> dict[str, Any]:
    blueprint = build_modern_cockpit_shell_blueprint()
    layout_verify = verify_modern_cockpit_layout_contract()
    failures: list[str] = []

    if not layout_verify["verification_ok"]:
        failures.extend(layout_verify["failures"])
    if blueprint["region_count"] != 4:
        failures.append("modern shell region count mismatch")
    if blueprint["runtime_truth_mutation_allowed"]:
        failures.append("runtime truth mutation drift")

    seen_regions: set[str] = set()
    for region in blueprint["shell_regions"]:
        if region["region_id"] in seen_regions:
            failures.append(f"duplicate region {region['region_id']}")
        seen_regions.add(region["region_id"])
        if not region["visible"]:
            failures.append(f"{region['region_id']} not visible")
        if not region["presentation_only"]:
            failures.append(f"{region['region_id']} presentation drift")
        if region["runtime_truth_mutation_allowed"]:
            failures.append(f"{region['region_id']} runtime truth mutation drift")
        if region["operator_mutation_enabled"]:
            failures.append(f"{region['region_id']} operator mutation enabled")

    return {
        "version": S46_R5_R12_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "region_count": blueprint["region_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }


def build_s46r5_r12_plateau_report() -> dict[str, Any]:
    blueprint = build_modern_cockpit_shell_blueprint()
    verification = verify_modern_cockpit_shell_blueprint()
    return {
        "version": S46_R5_R12_VERSION,
        "phase": "S46R9-R12",
        "status": "s46r5_r12_ready" if verification["verification_ok"] else "s46r5_r12_blocked",
        "ready": verification["verification_ok"],
        "blueprint": blueprint,
        "verification": verification,
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "next_phase": "S47 operator live status zones and cockpit payload aggregation",
    }
