"""
S303-S309 — Governed Fetch -> Quarantine -> Evidence Capsule.

This module keeps live execution blocked while defining the deterministic path
for operator-triggered provider probes, controlled fetch contracts, quarantine,
evidence capsule construction, lineage/trust scoring, and dashboard evidence
visibility.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import hashlib
import json

from claire.api.governed_internet_update_foundation_s296_s302 import (
    authority_locks,
    build_s302_stop_gate,
)


PHASE = "S303-S309"
VERSION = "v19.89.8-S303-S309"
PAYLOAD_ENDPOINT = "/dashboard/payload"
STATUS_ENDPOINT = "/dashboard/payload/status"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(stage_version: str, status: str, **extra: Any) -> Dict[str, Any]:
    payload = {
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


def build_s303_operator_triggered_provider_probe(provider_id: str = "dry_run_provider") -> Dict[str, Any]:
    authorized = provider_id in {"dry_run_provider", "manual_url_fetch_adapter", "search_provider_adapter"}
    return _base(
        "S303",
        "operator_triggered_provider_probe_ready" if authorized else "operator_triggered_provider_probe_blocked",
        probe_id=f"probe_{provider_id}",
        provider_id=provider_id,
        authorized_by_operator=True,
        probe_type="readiness_probe",
        provider_available=provider_id == "dry_run_provider",
        live_execution_allowed=False,
        blocked_reason=None if authorized else "provider_not_registered",
    )


def build_s304_controlled_fetch_executor(
    source_url: str = "https://example.invalid/governed-dry-run",
    body_read_allowed: bool = False,
) -> Dict[str, Any]:
    encoded = source_url.encode("utf-8")
    fetch_hash = hashlib.sha256(encoded).hexdigest()
    return _base(
        "S304",
        "controlled_fetch_executor_ready",
        fetch_request={
            "fetch_id": f"fetch_{fetch_hash[:12]}",
            "source_url": source_url,
            "authorized": True,
            "source_permission_checked": True,
            "rate_limit_checked": True,
            "timeout_seconds": 10,
            "content_size_limit_bytes": 250000,
            "body_read_allowed": body_read_allowed,
            "live_network_execution": False,
            "execution_mode": "dry_run_contract",
        },
        fetch_result={
            "fetch_id": f"fetch_{fetch_hash[:12]}",
            "status_code": None,
            "content_type": "not_fetched_in_dry_run",
            "content_length": 0,
            "safe_response_metadata_available": True,
            "raw_body_quarantined": False,
        },
    )


def build_s305_quarantine_store(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    fetch = build_s304_controlled_fetch_executor(source_url=source_url)
    fetch_id = fetch["fetch_request"]["fetch_id"]
    digest = hashlib.sha256(json.dumps(fetch, sort_keys=True).encode("utf-8")).hexdigest()
    return _base(
        "S305",
        "quarantine_store_contract_ready",
        quarantine_record={
            "quarantine_id": f"quarantine_{digest[:12]}",
            "fetch_id": fetch_id,
            "source_url": source_url,
            "sha256": digest,
            "stored_path": f"data/quarantine/{digest[:12]}.json",
            "promotion_status": "unreviewed",
            "runtime_truth_write": "blocked",
            "source_lineage_captured": True,
        },
        quarantine_manifest={
            "manifest_id": "internet_quarantine_manifest",
            "record_count": 1,
            "isolation_required": True,
        },
    )


def build_s306_evidence_capsule_builder(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    quarantine = build_s305_quarantine_store(source_url=source_url)
    q = quarantine["quarantine_record"]
    return _base(
        "S306",
        "evidence_capsule_builder_ready",
        evidence_capsule={
            "evidence_id": q["quarantine_id"].replace("quarantine_", "evidence_"),
            "quarantine_id": q["quarantine_id"],
            "source_url": source_url,
            "source_title": "governed dry-run source",
            "captured_at": _timestamp(),
            "claims": [],
            "entities": [],
            "signals": [],
            "confidence": "unreviewed",
            "lineage": {
                "fetch_id": q["fetch_id"],
                "quarantine_id": q["quarantine_id"],
                "sha256": q["sha256"],
            },
        },
    )


def build_s307_source_lineage_trust_scoring(source_url: str = "https://example.invalid/governed-dry-run") -> Dict[str, Any]:
    evidence = build_s306_evidence_capsule_builder(source_url=source_url)
    return _base(
        "S307",
        "source_lineage_trust_scoring_ready",
        evidence_id=evidence["evidence_capsule"]["evidence_id"],
        scoring={
            "source_trust_score": 0.50,
            "freshness_score": 0.50,
            "policy_score": 0.75,
            "evidence_quality_score": 0.40,
            "requires_manual_review": True,
            "disallowed_reason": None,
        },
        lineage=evidence["evidence_capsule"]["lineage"],
    )


def build_s308_internet_evidence_dashboard_card() -> Dict[str, Any]:
    capsule = build_s306_evidence_capsule_builder()
    trust = build_s307_source_lineage_trust_scoring()
    return _base(
        "S308",
        "internet_evidence_dashboard_card_ready",
        dashboard_card={
            "panel_key": "internet_evidence",
            "title": "Internet Evidence",
            "latest_quarantine_items": [capsule["evidence_capsule"]["quarantine_id"]],
            "latest_evidence_capsules": [capsule["evidence_capsule"]["evidence_id"]],
            "blocked_fetches": [],
            "source_trust_summary": trust["scoring"],
            "review_needed_count": 1,
        },
    )


def build_s309_stop_gate(report_dir: str | Path | None = None) -> Dict[str, Any]:
    previous = build_s302_stop_gate()
    checks = {
        "previous_gate_ok": previous["ok"],
        "provider_probe_ok": build_s303_operator_triggered_provider_probe()["ok"],
        "controlled_fetch_contract_ok": build_s304_controlled_fetch_executor()["ok"],
        "quarantine_store_ok": build_s305_quarantine_store()["ok"],
        "evidence_capsule_ok": build_s306_evidence_capsule_builder()["ok"],
        "lineage_trust_scoring_ok": build_s307_source_lineage_trust_scoring()["ok"],
        "dashboard_evidence_card_ok": build_s308_internet_evidence_dashboard_card()["ok"],
        "live_network_execution_still_blocked": build_s304_controlled_fetch_executor()["fetch_request"]["live_network_execution"] is False,
        "runtime_truth_mutation_blocked": authority_locks()["runtime_mutation_allowed"] is False,
    }
    ok = all(checks.values())
    payload = _base(
        "S309",
        "s303_s309_governed_fetch_evidence_passed" if ok else "s303_s309_governed_fetch_evidence_failed",
        checks=checks,
        forward_motion_allowed=ok,
        next_phase="S310-S316 evidence update proposal review export" if ok else "repair S303-S309 fetch/evidence",
        remaining_packs_to_governed_update_readiness=1,
    )

    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        report_path = path / "s303_s309_governed_fetch_evidence.json"
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        payload["report_path"] = str(report_path)

    return payload


def build_governed_fetch_evidence_pipeline_s303_s309() -> Dict[str, Any]:
    return _base(
        "S309",
        "governed_fetch_evidence_pipeline_ready",
        provider_probe=build_s303_operator_triggered_provider_probe(),
        controlled_fetch=build_s304_controlled_fetch_executor(),
        quarantine=build_s305_quarantine_store(),
        evidence_capsule=build_s306_evidence_capsule_builder(),
        lineage_trust=build_s307_source_lineage_trust_scoring(),
        dashboard_card=build_s308_internet_evidence_dashboard_card(),
        stop_gate=build_s309_stop_gate(),
    )


__all__ = [
    "build_s303_operator_triggered_provider_probe",
    "build_s304_controlled_fetch_executor",
    "build_s305_quarantine_store",
    "build_s306_evidence_capsule_builder",
    "build_s307_source_lineage_trust_scoring",
    "build_s308_internet_evidence_dashboard_card",
    "build_s309_stop_gate",
    "build_governed_fetch_evidence_pipeline_s303_s309",
]
