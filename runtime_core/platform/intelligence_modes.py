from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODES = {
    "deterministic": {
        "label": "Deterministic",
        "description": "Air-gapped local source-backed operation.",
        "operator_purpose": "Use local project files, runtime memory, source packs, and governed lifecycle logic without internet activation.",
        "requires_provider": False,
        "requires_validated_connected_run": False,
        "primary_actions": [
            "ask_claire",
            "run_local_lifecycle",
            "search_local_knowledge",
            "review_portfolio_outputs",
        ],
    },
    "connected": {
        "label": "Connected",
        "description": "One governed real provider active for metadata-only signal ingestion.",
        "operator_purpose": "Run metadata-only outside-signal discovery through quarantine and manual review.",
        "requires_provider": True,
        "requires_validated_connected_run": False,
        "primary_actions": [
            "prepare_metadata_query",
            "run_governed_provider_query",
            "review_quarantined_evidence",
            "promote_reviewed_evidence",
        ],
    },
    "hybrid": {
        "label": "Hybrid",
        "description": "Local source-backed intelligence fused with validated connected signals.",
        "operator_purpose": "Fuse local intelligence with promoted connected evidence after at least one validated connected run.",
        "requires_provider": True,
        "requires_validated_connected_run": True,
        "primary_actions": [
            "select_promoted_evidence",
            "run_hybrid_lifecycle",
            "compare_local_vs_connected_confidence",
            "produce_operator_decision_brief",
        ],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def latest_connected_validated_run(root: Path) -> bool:
    run_dir = root / "data" / "runs"
    if not run_dir.exists():
        return False
    for path in sorted(run_dir.glob("*/core_output.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:20]:
        try:
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        authority = payload.get("source_authority") if isinstance(payload, dict) else {}
        quality = payload.get("run_quality") if isinstance(payload, dict) else {}
        if isinstance(authority, dict) and isinstance(quality, dict):
            if authority.get("live_evidence_present") and quality.get("live_truth_eligible"):
                return True
    return False


def _mode_readiness(mode: str, provider_ready: bool, connected_validated: bool) -> dict[str, Any]:
    platform_ready = True
    execution_blockers: list[str] = []
    if mode in {"connected", "hybrid"} and not provider_ready:
        execution_blockers.append("governed_provider_not_ready")
    if mode == "hybrid" and not connected_validated:
        execution_blockers.append("validated_connected_run_required")

    operator_state = "ready_to_execute" if not execution_blockers else "ready_to_activate"
    if mode == "deterministic":
        operator_state = "ready_to_execute"

    return {
        "platform_ready": platform_ready,
        "operator_surface_ready": True,
        "activation_ready": True,
        "execution_ready": not execution_blockers,
        "operator_state": operator_state,
        "activation_blockers": [],
        "execution_blockers": execution_blockers,
    }


def build_intelligence_mode_state(project_root: Path | str | None = None) -> dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    try:
        from runtime_core.api.governed_connected_search import provider_state

        provider = provider_state()
    except Exception:
        provider = {"execution_allowed": False, "provider": "none"}

    provider_ready = bool(provider.get("execution_allowed") or any(
        item.get("execution_allowed") for item in provider.get("provider_stack_states", [])
    ))
    connected_validated = latest_connected_validated_run(root)
    modes = {}
    for key, config in MODES.items():
        readiness = _mode_readiness(key, provider_ready, connected_validated)
        enabled = True
        blockers: list[str] = []
        if config["requires_provider"] and not provider_ready:
            enabled = False
            blockers.append("governed_provider_not_ready")
        if config["requires_validated_connected_run"] and not connected_validated:
            enabled = False
            blockers.append("validated_connected_run_required")
        modes[key] = {
            **config,
            "mode": key,
            "enabled": enabled,
            "blockers": blockers,
            "readiness": readiness,
            "platform_ready": readiness["platform_ready"],
            "operator_surface_ready": readiness["operator_surface_ready"],
            "activation_ready": readiness["activation_ready"],
            "execution_ready": readiness["execution_ready"],
            "operator_state": readiness["operator_state"],
        }
    active = "hybrid" if modes["hybrid"]["enabled"] else "connected" if modes["connected"]["enabled"] else "deterministic"
    platform_mode_completion = round(
        sum(1 for item in modes.values() if item["platform_ready"] and item["operator_surface_ready"]) / len(modes) * 100,
        1,
    )
    activation_mode_completion = round(
        sum(1 for item in modes.values() if item["activation_ready"]) / len(modes) * 100,
        1,
    )
    live_execution_completion = round(
        sum(1 for item in modes.values() if item["execution_ready"]) / len(modes) * 100,
        1,
    )
    return {
        "schema_version": "claire_intelligence_modes_v1",
        "status": "ready",
        "active_mode": active,
        "operator_selectable_modes": modes,
        "platform_mode_completion_percent": platform_mode_completion,
        "activation_mode_completion_percent": activation_mode_completion,
        "live_execution_completion_percent": live_execution_completion,
        "provider_ready": provider_ready,
        "connected_validated": connected_validated,
        "provider": provider,
        "unlock_contract": {
            "deterministic": "platform-ready now; no provider required",
            "connected": "operator surface is ready before internet activation; execution enables when one governed provider has execution_allowed=true",
            "hybrid": "operator surface is ready before internet activation; execution enables after connected mode produces at least one live_truth_eligible run",
        },
        "operator_workflow_order": [
            "finish_platform_and_dashboard_operator_surface",
            "activate_governed_provider",
            "run_connected_metadata_query",
            "review_and_promote_evidence",
            "unlock_hybrid_validation_cycle",
        ],
        "generated_at": utc_now(),
    }
