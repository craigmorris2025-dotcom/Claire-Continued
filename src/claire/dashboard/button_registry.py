"""Dashboard action button registry.

This module defines the governed UI action surface for Claire's dashboard.
It is intentionally data-driven so tests can prove that dashboard actions map
only to bounded backend routes and never execute arbitrary commands.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass(frozen=True)
class DashboardActionButton:
    id: str
    label: str
    category: str
    method: str
    route: str
    description: str
    requires_confirmation: bool = False
    governance_scope: str = "dashboard_runtime_alignment"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


BUTTONS: List[DashboardActionButton] = [
    DashboardActionButton(
        id="health_check",
        label="Check Runtime Health",
        category="Runtime",
        method="GET",
        route="/health",
        description="Verify the running backend health endpoint.",
    ),
    DashboardActionButton(
        id="dashboard_alignment",
        label="Verify Dashboard Alignment",
        category="Dashboard",
        method="GET",
        route="/dashboard/alignment/status",
        description="Compare dashboard surfaces to installed governed runtime capabilities.",
    ),
    DashboardActionButton(
        id="dashboard_capabilities",
        label="Load Capability Manifest",
        category="Dashboard",
        method="GET",
        route="/dashboard/alignment/capabilities",
        description="Load the dashboard capability manifest created by v17.50.",
    ),
    DashboardActionButton(
        id="internet_operations",
        label="Open Internet Operations State",
        category="Internet Operations",
        method="GET",
        route="/internet/operations/status",
        description="Read governed internet operations state if the v17.47 dashboard route is mounted.",
    ),
    DashboardActionButton(
        id="campaigns_status",
        label="Check Campaign Runtime",
        category="Campaigns",
        method="GET",
        route="/internet/campaigns/status",
        description="Read persistent campaign runtime state if the v17.43+ route is mounted.",
    ),
    DashboardActionButton(
        id="source_trust_status",
        label="Check Source Trust",
        category="Source Trust",
        method="GET",
        route="/internet/source-trust/status",
        description="Read adaptive source trust state if the v17.46 route is mounted.",
    ),
    DashboardActionButton(
        id="deployment_status",
        label="Check Deployment Hardening",
        category="Deployment",
        method="GET",
        route="/deployment/status",
        description="Read deployment hardening state if the v17.48 route is mounted.",
    ),
    DashboardActionButton(
        id="launch_lock_status",
        label="Check Launch Regression Lock",
        category="Launch Lock",
        method="GET",
        route="/launch/regression-lock/status",
        description="Read launch regression lock state if the v17.49 route is mounted.",
    ),
]


def get_button_registry() -> List[Dict[str, object]]:
    return [button.to_dict() for button in BUTTONS]


def get_button_by_id(button_id: str) -> Dict[str, object]:
    for button in BUTTONS:
        if button.id == button_id:
            return button.to_dict()
    raise KeyError(f"Unknown dashboard button: {button_id}")


def validate_button_registry() -> Dict[str, object]:
    ids = [button.id for button in BUTTONS]
    routes = [button.route for button in BUTTONS]
    unsafe = [button.to_dict() for button in BUTTONS if button.method not in {"GET", "POST"}]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    invalid_routes = sorted(route for route in routes if not route.startswith("/"))
    return {
        "status": "ok" if not unsafe and not duplicate_ids and not invalid_routes else "failed",
        "button_count": len(BUTTONS),
        "duplicate_ids": duplicate_ids,
        "invalid_routes": invalid_routes,
        "unsafe_methods": unsafe,
    }
