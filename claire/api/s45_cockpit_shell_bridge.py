from __future__ import annotations

from typing import Any

from claire.api.s45_cockpit_ui_bridge import (
    S45_VERSION,
    build_cockpit_ui_bridge_manifest,
    verify_cockpit_ui_bridge_manifest,
)
from claire.api.s45_operator_visible_panels import (
    build_operator_visible_panel_bindings,
    verify_operator_visible_panel_bindings,
)


S45_R9_R16_VERSION = "v19.89.8-S45R9-R16"
SHELL_ASSET_PATH = "frontend/cockpit/s45_bridge/cockpit_shell_bridge.html"
SHELL_JS_PATH = "frontend/cockpit/s45_bridge/s45_shell_mount.js"
SHELL_CSS_PATH = "frontend/cockpit/s45_bridge/s45_shell_mount.css"


def build_cockpit_shell_bridge_manifest() -> dict[str, Any]:
    ui_bridge = build_cockpit_ui_bridge_manifest()
    panels = build_operator_visible_panel_bindings()

    shell_mounts = []
    for panel in panels["panels"]:
        shell_mounts.append({
            "mount_id": panel["panel_id"],
            "surface_id": panel["surface_id"],
            "group_id": panel["group_id"],
            "title": panel["title"],
            "fetch_path": panel["fetch_path"],
            "method": "GET",
            "render_mode": "read_only_operator_card",
            "response_mode": "read_only_artifact",
            "target_selector": f"#{panel['panel_id']}",
            "mounted": True,
            "visible_to_operator": True,
            "backend_owns_truth": True,
            "cockpit_presentation_only": True,
            "presentation_only": True,
            "read_only": True,
            "runtime_truth_mutation_allowed": False,
            "runtime_mutation_allowed": False,
            "operator_mutation_enabled": False,
            "autonomous_execution_enabled": False,
            "automatic_updates_enabled": False,
            "browser_execution_enabled": False,
            "javascript_execution_authority": "presentation_only",
        })

    return {
        "version": S45_R9_R16_VERSION,
        "phase": "S45R9-R10",
        "status": "cockpit_shell_bridge_manifest_ready",
        "source_ui_bridge_version": ui_bridge["version"],
        "shell_asset_path": SHELL_ASSET_PATH,
        "shell_js_path": SHELL_JS_PATH,
        "shell_css_path": SHELL_CSS_PATH,
        "shell_mount_count": len(shell_mounts),
        "shell_mounts": shell_mounts,
        "panel_group_count": len(panels["groups"]),
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "autonomous_execution_enabled": False,
        "automatic_updates_enabled": False,
        "browser_execution_enabled": False,
        "next_phase": "S45R11-R12 panel data mounting contracts",
    }


def verify_cockpit_shell_bridge_manifest() -> dict[str, Any]:
    manifest = build_cockpit_shell_bridge_manifest()
    ui_verify = verify_cockpit_ui_bridge_manifest()
    panel_verify = verify_operator_visible_panel_bindings()

    failures: list[Any] = []
    if not ui_verify["verification_ok"]:
        failures.extend(ui_verify["failures"])
    if not panel_verify["verification_ok"]:
        failures.extend(panel_verify["failures"])
    if manifest["shell_mount_count"] != 7:
        failures.append("shell mount count mismatch")
    if manifest["runtime_truth_mutation_allowed"]:
        failures.append("runtime truth mutation allowed")

    seen_mounts: set[str] = set()
    for mount in manifest["shell_mounts"]:
        if mount["mount_id"] in seen_mounts:
            failures.append(f"duplicate shell mount {mount['mount_id']}")
        seen_mounts.add(mount["mount_id"])
        if mount["method"] != "GET":
            failures.append(f"{mount['mount_id']} method drift")
        if not mount["mounted"]:
            failures.append(f"{mount['mount_id']} not mounted")
        if not mount["presentation_only"]:
            failures.append(f"{mount['mount_id']} presentation drift")
        if mount["runtime_truth_mutation_allowed"]:
            failures.append(f"{mount['mount_id']} runtime truth mutation drift")
        if mount["operator_mutation_enabled"]:
            failures.append(f"{mount['mount_id']} operator mutation enabled")

    return {
        "version": S45_R9_R16_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "shell_mount_count": manifest["shell_mount_count"],
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_mutation_allowed": False,
    }
