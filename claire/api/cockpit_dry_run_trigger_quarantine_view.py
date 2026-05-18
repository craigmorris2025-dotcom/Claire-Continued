"""Cockpit dry-run trigger readiness and evidence quarantine view.

S33R5 is passive. It does not execute a probe, register an endpoint, perform
network access, read response bodies, mutate runtime truth, launch a browser,
trigger autonomous behavior, or apply updates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_cockpit_dry_run_trigger_and_quarantine_view() -> Dict[str, Any]:
    controls: List[Dict[str, Any]] = [
        {
            "id": "metadata_probe_dry_run_trigger",
            "label": "Metadata probe dry-run trigger",
            "state": "visible_disabled",
            "authority": "operator_visible_only",
            "reason": (
                "No guarded endpoint has been registered yet. The cockpit may "
                "show the trigger as unavailable until a safe mounted router is proven."
            ),
        },
        {
            "id": "evidence_quarantine_view",
            "label": "Evidence quarantine",
            "state": "visible_empty",
            "authority": "read_only_presentation",
            "reason": (
                "Evidence remains quarantined and empty because no live execution "
                "or body read is enabled in S33R5."
            ),
        },
    ]

    return {
        "version": "v19.89.8-S33R5",
        "status": "cockpit_dry_run_trigger_readiness_visible",
        "generated_at_utc": _iso_now(),
        "route_registered": False,
        "dry_run_trigger_enabled": False,
        "dry_run_execution_enabled": False,
        "evidence_quarantine_visible": True,
        "evidence_quarantine_items": [],
        "manual_promotion_required": True,
        "runtime_authority": "blocked",
        "browser_execution_authority": "blocked",
        "runtime_truth_mutation": "blocked",
        "autonomous_execution": "blocked",
        "automatic_updates": "blocked",
        "network_request": "blocked",
        "response_body_reads": "blocked",
        "live_web_execution": "blocked_until_explicitly_gated",
        "controls": controls,
        "operator_message": (
            "Dry-run trigger and quarantine surfaces are ready for cockpit presentation, "
            "but execution remains blocked."
        ),
    }
