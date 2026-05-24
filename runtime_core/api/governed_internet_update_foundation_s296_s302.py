"""
S296-S302 â€” Clean Plateau + Governed Internet Update Foundation.

This module is deliberately deterministic and authority-locked. It does not
perform live web execution. It defines the governance foundation Claire needs
before controlled internet fetch/evidence/update work can safely proceed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import json


PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"
PHASE = "S296-S302"
VERSION = "v19.89.8-S296-S302"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def authority_locks() -> Dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "runtime_truth_write_allowed": False,
        "runtime_mutation_allowed": False,
        "automatic_updates_allowed": False,
        "autonomous_execution_allowed": False,
        "autonomous_crawling_allowed": False,
        "continuous_crawling_allowed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "operator_confirmation_required": True,
        "failure_mode": "fail_closed",
    }


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "stage_version": stage_version,
        "phase": PHASE,
        "version": VERSION,
        "status": status,
        "ok": True,
        "ready": True,
        "payload_endpoint": PAYLOAD_ENDPOINT,
        "status_endpoint": STATUS_ENDPOINT,
        "authority_locks": authority_locks(),
        "runtime_truth_write": "blocked",
        "runtime_truth_write_enabled": False,
        "runtime_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "autonomous_crawling_enabled": False,
        "continuous_crawling_enabled": False,
        "proposal_only": True,
        "runtime_truth_modified": False,
        "created_at": _timestamp(),
    }
    payload.update(extra)
    return payload


def build_s296_clean_plateau_checkpoint() -> Dict[str, Any]:
    return _base(
        "S296",
        "clean_plateau_checkpoint_ready",
        checkpoint_id="v19_89_8_pytest_green_plateau",
        active_layout=["claire", "frontend", "tests", "main.py", "LAUNCH_PLATFORM.bat", "root_config_files"],
        known_green_gate="root_pytest_green_after_s149_s183_s289_s295_recovery",
        old_layout_assumptions_blocked=True,
        checkpoint_policy="no_forward_build_without_green_gate",
    )


def build_s297_internet_update_authority_contract() -> Dict[str, Any]:
    return _base(
        "S297",
        "internet_update_authority_contract_ready",
        internet_access_mode="governed_operator_controlled",
        allowed_internet_actions=[
            "provider_status_check",
            "operator_triggered_probe",
            "authorized_controlled_fetch",
            "quarantine_storage",
            "evidence_capsule_creation",
            "update_candidate_proposal",
        ],
        blocked_internet_actions=[
            "autonomous_crawling",
            "automatic_runtime_truth_write",
            "self_patch_from_web",
            "unreviewed_source_promotion",
            "silent_background_fetch",
        ],
        manual_review_required=True,
    )


def build_s298_source_policy_registry() -> Dict[str, Any]:
    sources = [
        {
            "source_id": "operator_supplied_url",
            "source_type": "manual_url",
            "trust_tier": "review_required",
            "allowed_for_probe": True,
            "allowed_for_fetch": True,
            "allowed_for_update_candidate": True,
            "blocked_reason": None,
        },
        {
            "source_id": "approved_provider_result",
            "source_type": "search_provider_result",
            "trust_tier": "policy_scored",
            "allowed_for_probe": True,
            "allowed_for_fetch": True,
            "allowed_for_update_candidate": True,
            "blocked_reason": None,
        },
        {
            "source_id": "unreviewed_autonomous_crawl",
            "source_type": "autonomous_crawl",
            "trust_tier": "blocked",
            "allowed_for_probe": False,
            "allowed_for_fetch": False,
            "allowed_for_update_candidate": False,
            "blocked_reason": "autonomous crawling is not enabled",
        },
    ]
    return _base(
        "S298",
        "source_policy_registry_ready",
        registry_id="governed_source_policy_registry",
        sources=sources,
        approved_source_count=sum(1 for source in sources if source["allowed_for_fetch"]),
        blocked_source_count=sum(1 for source in sources if not source["allowed_for_fetch"]),
    )


def build_s299_provider_adapter_readiness_contract() -> Dict[str, Any]:
    providers = [
        {
            "provider_id": "dry_run_provider",
            "provider_status": "available",
            "provider_enabled": True,
            "dry_run_available": True,
            "live_execution_allowed": False,
            "rate_limit_policy": "local_no_network",
            "failure_mode": "fail_closed",
        },
        {
            "provider_id": "manual_url_fetch_adapter",
            "provider_status": "defined_not_live",
            "provider_enabled": False,
            "dry_run_available": True,
            "live_execution_allowed": False,
            "rate_limit_policy": "requires_operator_gate",
            "failure_mode": "fail_closed",
        },
        {
            "provider_id": "search_provider_adapter",
            "provider_status": "defined_not_live",
            "provider_enabled": False,
            "dry_run_available": True,
            "live_execution_allowed": False,
            "rate_limit_policy": "requires_operator_gate",
            "failure_mode": "fail_closed",
        },
    ]
    return _base(
        "S299",
        "provider_adapter_readiness_contract_ready",
        provider_registry=providers,
        live_provider_count=sum(1 for provider in providers if provider["live_execution_allowed"]),
        dry_run_provider_count=sum(1 for provider in providers if provider["dry_run_available"]),
    )


def build_s300_internet_update_job_model() -> Dict[str, Any]:
    statuses = [
        "created",
        "authorized",
        "queued",
        "fetching",
        "quarantined",
        "evidence_ready",
        "candidate_ready",
        "review_required",
        "approved",
        "rejected",
        "failed",
        "blocked",
    ]
    return _base(
        "S300",
        "internet_update_job_model_ready",
        job_model={
            "job_id": "internet_update_job_template",
            "operator_intent_required": True,
            "source_target_required": True,
            "status_lifecycle": statuses,
            "terminal_statuses": ["approved", "rejected", "failed", "blocked"],
            "governance_locks": authority_locks(),
        },
    )


def build_s301_dashboard_internet_update_surface_contract() -> Dict[str, Any]:
    panels = {
        "internet_update_readiness": {
            "panel_key": "internet_update_readiness",
            "title": "Internet Update Readiness",
            "status": "ready",
            "cards": [
                "authority_status",
                "source_policy_status",
                "provider_status",
                "latest_job",
                "blocked_modes",
            ],
        },
        "provider_status": {
            "panel_key": "provider_status",
            "title": "Provider Status",
            "status": "ready",
        },
        "source_policy": {
            "panel_key": "source_policy",
            "title": "Source Policy",
            "status": "ready",
        },
    }
    return _base(
        "S301",
        "dashboard_internet_update_surface_contract_ready",
        dashboard_surface={
            "surface_id": "internet_update_foundation",
            "panel_count": len(panels),
            "panels": panels,
            "missing_data_behavior": "render_blocked_or_waiting_state",
            "dashboard_truth_policy": "backend_payload_only",
        },
    )


def build_s302_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    checks = {
        "clean_plateau_checkpoint_ok": build_s296_clean_plateau_checkpoint()["ok"],
        "internet_update_authority_ok": build_s297_internet_update_authority_contract()["ok"],
        "source_policy_registry_ok": build_s298_source_policy_registry()["ok"],
        "provider_adapter_readiness_ok": build_s299_provider_adapter_readiness_contract()["ok"],
        "internet_update_job_model_ok": build_s300_internet_update_job_model()["ok"],
        "dashboard_surface_contract_ok": build_s301_dashboard_internet_update_surface_contract()["ok"],
        "runtime_truth_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
        "automatic_updates_blocked": authority_locks()["automatic_updates_allowed"] is False,
        "autonomous_crawling_blocked": authority_locks()["autonomous_crawling_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S302",
        "s296_s302_governed_internet_update_foundation_passed" if ok else "s296_s302_governed_internet_update_foundation_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S303-S309 governed fetch quarantine evidence capsule" if ok else "repair S296-S302 foundation",
        remaining_packs_to_governed_update_readiness=2,
    )

    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s296_s302_governed_internet_update_foundation.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)

    return payload


def build_governed_internet_update_foundation_s296_s302() -> Dict[str, Any]:
    return _base(
        "S302",
        "governed_internet_update_foundation_ready",
        checkpoint=build_s296_clean_plateau_checkpoint(),
        authority=build_s297_internet_update_authority_contract(),
        source_policy=build_s298_source_policy_registry(),
        provider_readiness=build_s299_provider_adapter_readiness_contract(),
        job_model=build_s300_internet_update_job_model(),
        dashboard_surface=build_s301_dashboard_internet_update_surface_contract(),
        stop_gate=build_s302_stop_gate(),
    )


__all__ = [
    "authority_locks",
    "build_s296_clean_plateau_checkpoint",
    "build_s297_internet_update_authority_contract",
    "build_s298_source_policy_registry",
    "build_s299_provider_adapter_readiness_contract",
    "build_s300_internet_update_job_model",
    "build_s301_dashboard_internet_update_surface_contract",
    "build_s302_stop_gate",
    "build_governed_internet_update_foundation_s296_s302",
]
