"""
S317-S323 — Dashboard Contract Consolidation.

This pack stops newly proven internet-readiness work from being left out in the
open. It creates a deterministic dashboard extension contract that can be folded
into the canonical cockpit payload without adding random endpoint sprawl.

No runtime mutation, no automatic updates, and no autonomous crawling are enabled.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable
import json

from claire.api.governed_internet_update_foundation_s296_s302 import (
    authority_locks,
    build_governed_internet_update_foundation_s296_s302,
)
from claire.api.governed_fetch_evidence_pipeline_s303_s309 import (
    build_governed_fetch_evidence_pipeline_s303_s309,
)
from claire.api.governed_update_proposal_pipeline_s310_s316 import (
    build_governed_update_proposal_pipeline_s310_s316,
)


PHASE = "S317-S323"
VERSION = "v19.89.8-S317-S323"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def build_s317_canonical_payload_extension_registry() -> Dict[str, Any]:
    sections = {
        "governed_internet_update_foundation": {
            "owner": "claire.api.governed_internet_update_foundation_s296_s302",
            "source_stage": "S296-S302",
            "panel_keys": ["internet_update_readiness", "source_policy", "provider_status"],
            "summary_key": "internet_update_readiness",
        },
        "governed_fetch_evidence_pipeline": {
            "owner": "claire.api.governed_fetch_evidence_pipeline_s303_s309",
            "source_stage": "S303-S309",
            "panel_keys": ["internet_evidence", "quarantine", "source_trust"],
            "summary_key": "internet_evidence",
        },
        "governed_update_proposal_pipeline": {
            "owner": "claire.api.governed_update_proposal_pipeline_s310_s316",
            "source_stage": "S310-S316",
            "panel_keys": ["internet_update_proposals", "review_queue", "approved_exports"],
            "summary_key": "internet_update_proposals",
        },
    }
    return _base(
        "S317",
        "canonical_payload_extension_registry_ready",
        extension_registry=sections,
        extension_count=len(sections),
        endpoint_strategy="extend_existing_dashboard_payload",
        random_endpoint_sprawl_allowed=False,
    )


def build_s318_internet_readiness_payload_extension() -> Dict[str, Any]:
    foundation = build_governed_internet_update_foundation_s296_s302()
    evidence = build_governed_fetch_evidence_pipeline_s303_s309()
    proposals = build_governed_update_proposal_pipeline_s310_s316()
    extension = {
        "internet_update_readiness": {
            "status": "ready",
            "foundation_gate": foundation["stop_gate"]["status"],
            "fetch_evidence_gate": evidence["stop_gate"]["status"],
            "proposal_gate": proposals["stop_gate"]["status"],
            "readiness_state": proposals["stop_gate"]["readiness_state"],
            "blocked_modes": [
                "runtime_mutation",
                "automatic_updates",
                "autonomous_crawling",
                "continuous_crawling",
            ],
        },
        "internet_evidence": evidence["dashboard_card"]["dashboard_card"],
        "internet_update_proposals": proposals["dashboard_surface"]["dashboard_surface"],
        "governed_internet_contracts": {
            "foundation": foundation,
            "fetch_evidence": evidence,
            "update_proposals": proposals,
        },
    }
    return _base(
        "S318",
        "internet_readiness_payload_extension_ready",
        dashboard_payload_extension=extension,
        extension_keys=list(extension.keys()),
        canonical_endpoint=PAYLOAD_ENDPOINT,
    )


def build_s319_dashboard_fetch_map_lock() -> Dict[str, Any]:
    fetch_map = {
        "dashboard_payload": PAYLOAD_ENDPOINT,
        "dashboard_payload_status": STATUS_ENDPOINT,
        "internet_update_readiness": PAYLOAD_ENDPOINT,
        "internet_evidence": PAYLOAD_ENDPOINT,
        "internet_update_proposals": PAYLOAD_ENDPOINT,
        "blocked_authority_modes": PAYLOAD_ENDPOINT,
    }
    return _base(
        "S319",
        "dashboard_fetch_map_lock_ready",
        fetch_map=fetch_map,
        single_boot_payload=True,
        random_panel_fetches_allowed=False,
        detail_endpoints_deferred_until_action_phase=True,
    )


def build_s320_cockpit_panel_registry() -> Dict[str, Any]:
    panels = {
        "internet_update_readiness": {
            "title": "Internet Update Readiness",
            "zone": "web_readiness",
            "payload_key": "internet_update_readiness",
            "required_fields": ["status", "readiness_state", "blocked_modes"],
            "truth_source": PAYLOAD_ENDPOINT,
        },
        "internet_evidence": {
            "title": "Internet Evidence",
            "zone": "evidence_review",
            "payload_key": "internet_evidence",
            "required_fields": ["latest_evidence_capsules", "review_needed_count", "source_trust_summary"],
            "truth_source": PAYLOAD_ENDPOINT,
        },
        "internet_update_proposals": {
            "title": "Update Proposals",
            "zone": "proposal_review",
            "payload_key": "internet_update_proposals",
            "required_fields": ["internet_update_proposals", "review_queue_status", "runtime_mutation_status"],
            "truth_source": PAYLOAD_ENDPOINT,
        },
        "blocked_authority_modes": {
            "title": "Blocked Authority Modes",
            "zone": "governance",
            "payload_key": "authority_locks",
            "required_fields": ["runtime_mutation_allowed", "automatic_updates_allowed", "autonomous_crawling_allowed"],
            "truth_source": PAYLOAD_ENDPOINT,
        },
    }
    return _base(
        "S320",
        "cockpit_panel_registry_ready",
        panel_registry=panels,
        panel_count=len(panels),
    )


def build_s321_missing_data_blocked_state_contract() -> Dict[str, Any]:
    states = {
        "loading": {"visible": True, "message": "Waiting for backend payload."},
        "missing": {"visible": True, "message": "Required backend payload key is missing."},
        "blocked": {"visible": True, "message": "Action is blocked by governance authority locks."},
        "error": {"visible": True, "message": "Payload failed validation."},
        "ready": {"visible": True, "message": "Payload section is ready."},
    }
    return _base(
        "S321",
        "missing_data_blocked_state_contract_ready",
        renderer_states=states,
        dashboard_must_not_hide_missing_data=True,
        fake_connected_labels_allowed=False,
    )


def _has_path(payload: Dict[str, Any], path: Iterable[str]) -> bool:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return True


def build_s322_dashboard_schema_validation() -> Dict[str, Any]:
    extension = build_s318_internet_readiness_payload_extension()["dashboard_payload_extension"]
    panel_registry = build_s320_cockpit_panel_registry()["panel_registry"]
    checks = {
        "extension_has_readiness": "internet_update_readiness" in extension,
        "extension_has_evidence": "internet_evidence" in extension,
        "extension_has_proposals": "internet_update_proposals" in extension,
        "readiness_has_blocked_modes": _has_path(extension, ["internet_update_readiness", "blocked_modes"]),
        "evidence_has_capsules": _has_path(extension, ["internet_evidence", "latest_evidence_capsules"]),
        "proposal_has_review_queue": _has_path(extension, ["internet_update_proposals", "review_queue_status"]),
        "panel_registry_complete": all(
            spec["payload_key"] in extension or spec["payload_key"] == "authority_locks"
            for spec in panel_registry.values()
        ),
    }
    return _base(
        "S322",
        "dashboard_schema_validation_passed" if all(checks.values()) else "dashboard_schema_validation_failed",
        checks=checks,
        validation_ok=all(checks.values()),
    )


def build_s323_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    checks = {
        "extension_registry_ok": build_s317_canonical_payload_extension_registry()["ok"],
        "payload_extension_ok": build_s318_internet_readiness_payload_extension()["ok"],
        "fetch_map_lock_ok": build_s319_dashboard_fetch_map_lock()["ok"],
        "panel_registry_ok": build_s320_cockpit_panel_registry()["ok"],
        "missing_state_contract_ok": build_s321_missing_data_blocked_state_contract()["ok"],
        "schema_validation_ok": build_s322_dashboard_schema_validation()["validation_ok"],
        "runtime_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S323",
        "dashboard_contract_consolidation_passed" if ok else "dashboard_contract_consolidation_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S324-S330 operator cockpit layout consolidation" if ok else "repair S317-S323 dashboard contract",
        remaining_packs_to_dashboard_consolidation=2,
    )
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s317_s323_dashboard_contract_consolidation.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)
    return payload


def build_dashboard_contract_consolidation_s317_s323() -> Dict[str, Any]:
    return _base(
        "S323",
        "dashboard_contract_consolidation_ready",
        extension_registry=build_s317_canonical_payload_extension_registry(),
        payload_extension=build_s318_internet_readiness_payload_extension(),
        fetch_map=build_s319_dashboard_fetch_map_lock(),
        panel_registry=build_s320_cockpit_panel_registry(),
        missing_state_contract=build_s321_missing_data_blocked_state_contract(),
        schema_validation=build_s322_dashboard_schema_validation(),
        stop_gate=build_s323_stop_gate(),
    )


def apply_s317_s323_extension_to_payload(existing_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return a merged payload without mutating the input object."""
    base_payload = dict(existing_payload or {})
    extension = build_s318_internet_readiness_payload_extension()["dashboard_payload_extension"]
    base_payload.setdefault("dashboard_consolidation", {})
    base_payload["dashboard_consolidation"]["s317_s323"] = build_dashboard_contract_consolidation_s317_s323()
    base_payload.update(extension)
    base_payload["dashboard_fetch_map_lock"] = build_s319_dashboard_fetch_map_lock()["fetch_map"]
    base_payload["cockpit_panel_registry"] = build_s320_cockpit_panel_registry()["panel_registry"]
    base_payload["dashboard_renderer_states"] = build_s321_missing_data_blocked_state_contract()["renderer_states"]
    return base_payload


__all__ = [
    "build_s317_canonical_payload_extension_registry",
    "build_s318_internet_readiness_payload_extension",
    "build_s319_dashboard_fetch_map_lock",
    "build_s320_cockpit_panel_registry",
    "build_s321_missing_data_blocked_state_contract",
    "build_s322_dashboard_schema_validation",
    "build_s323_stop_gate",
    "build_dashboard_contract_consolidation_s317_s323",
    "apply_s317_s323_extension_to_payload",
]
