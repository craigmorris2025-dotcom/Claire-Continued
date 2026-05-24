
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "v17.85"
CONTRACT_NAME = "Governed Web Evidence Promotion Gate"

LIVE_PROBE_RESULT_PATH = Path("data/internet_live_probe/last_live_probe_result.json")
LIVE_PROBE_EVIDENCE_LOG_PATH = Path("data/internet_live_probe/live_probe_evidence_log.json")
LIVE_PROBE_QUARANTINE_LOG_PATH = Path("data/internet_live_probe/live_probe_quarantine_log.json")
PROVIDER_GATE_PATH = Path("data/internet_provider/provider_configuration_gate.json")
ALLOWLIST_PATH = Path("data/internet_provider/source_allowlist_template.json")
QUARANTINE_POLICY_PATH = Path("data/internet_provider/quarantine_policy.json")

PROMOTION_GATE_PATH = Path("data/internet_evidence/evidence_promotion_gate.json")
PROMOTION_TEMPLATE_PATH = Path("data/internet_evidence/promoted_evidence_candidates_template.json")
QUARANTINE_REVIEW_QUEUE_PATH = Path("data/internet_evidence/quarantine_review_queue.json")
PROMOTED_STORE_PATH = Path("data/internet_evidence/promoted_evidence_store.json")
PROMOTION_EXECUTION_REPORT_PATH = Path("data/internet_evidence/evidence_promotion_execution_report.json")
DASHBOARD_PAYLOAD_PATH = Path("data/dashboard/internet_evidence_promotion_payload.json")
STOP_GO_PATH = Path("data/internet_evidence/v17_85_evidence_promotion_stop_go.json")
STOP_GO_MD_PATH = Path("data/internet_evidence/v17_85_evidence_promotion_stop_go.md")

CONFIRM_TEXT = "PROMOTE REVIEWED EVIDENCE"

GOVERNANCE = {
    "promotion_gate_only": True,
    "manual_review_required": True,
    "no_runtime_truth_auto_ingestion": True,
    "no_unreviewed_quarantine_promotion": True,
    "no_automatic_update_execution": True,
    "no_autonomous_agent_execution": True,
    "source_url_required": True,
    "retrieval_timestamp_required": True,
    "domain_trust_status_required": True,
    "operator_notes_required_for_promotion": True,
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_json(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not path.exists():
        return {}, {"path": str(path).replace("\\", "/"), "status": "missing"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": "JSON root is not object"}
        return payload, {"path": str(path).replace("\\", "/"), "status": "loaded"}
    except Exception as exc:
        return {}, {"path": str(path).replace("\\", "/"), "status": "invalid", "error": str(exc)}


def append_records(path: Path, records: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    existing, _ = read_json(path)
    current = existing.get("records") if isinstance(existing.get("records"), list) else []
    current.extend(records)
    payload = {
        "version": VERSION,
        "updated_at": now(),
        "metadata": metadata or {},
        "records": current,
    }
    write_json(path, payload)
    return payload


def domain_from_url(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = (urlparse(url).netloc or "").lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def load_live_probe_records(root: Path) -> Dict[str, Any]:
    last, last_source = read_json(root / LIVE_PROBE_RESULT_PATH)
    evidence_log, evidence_source = read_json(root / LIVE_PROBE_EVIDENCE_LOG_PATH)
    quarantine_log, quarantine_source = read_json(root / LIVE_PROBE_QUARANTINE_LOG_PATH)

    records: List[Dict[str, Any]] = []
    if isinstance(last.get("results"), list):
        for item in last["results"]:
            if isinstance(item, dict):
                records.append({**item, "source_record": "last_live_probe_result"})

    evidence_records = evidence_log.get("records") if isinstance(evidence_log.get("records"), list) else []
    for event in evidence_records:
        if isinstance(event, dict) and isinstance(event.get("results"), list):
            for item in event["results"]:
                if isinstance(item, dict):
                    records.append({**item, "source_record": "live_probe_evidence_log", "query": event.get("query")})

    quarantine_records: List[Dict[str, Any]] = []
    quarantine_events = quarantine_log.get("records") if isinstance(quarantine_log.get("records"), list) else []
    for event in quarantine_events:
        if isinstance(event, dict) and isinstance(event.get("records"), list):
            for item in event["records"]:
                if isinstance(item, dict):
                    quarantine_records.append({**item, "source_record": "live_probe_quarantine_log", "query": event.get("query")})

    seen = set()
    deduped: List[Dict[str, Any]] = []
    for item in records:
        key = (item.get("url", ""), item.get("title", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    seen_q = set()
    deduped_q: List[Dict[str, Any]] = []
    for item in quarantine_records:
        key = (item.get("url", ""), item.get("title", ""))
        if key in seen_q:
            continue
        seen_q.add(key)
        deduped_q.append(item)

    return {
        "sources": {
            "last_result": last_source,
            "evidence_log": evidence_source,
            "quarantine_log": quarantine_source,
        },
        "last_result_status": last.get("status", "missing"),
        "last_result_executed": last.get("executed", False),
        "record_count": len(deduped),
        "quarantine_count": len(deduped_q),
        "records": deduped,
        "quarantine_records": deduped_q,
    }


def evidence_candidate(record: Dict[str, Any], idx: int) -> Dict[str, Any]:
    url = str(record.get("url") or "")
    domain = str(record.get("source_domain") or domain_from_url(url))
    quarantined = bool(record.get("quarantined", False))
    trust_status = str(record.get("trust_status") or ("unknown_quarantined" if quarantined else "unknown"))
    return {
        "candidate_id": f"web_evidence_{idx:04d}",
        "approved_for_promotion": False,
        "operator_notes": "",
        "promotion_target": "reviewed_web_evidence_store",
        "may_feed_runtime_truth": False,
        "requires_later_runtime_truth_gate": True,
        "title": str(record.get("title") or ""),
        "url": url,
        "source_domain": domain,
        "snippet": str(record.get("snippet") or "")[:1200],
        "retrieved_at": str(record.get("retrieved_at") or ""),
        "provider": str(record.get("provider") or ""),
        "query": str(record.get("query") or ""),
        "trust_status": trust_status,
        "quarantined": quarantined,
        "source_record": str(record.get("source_record") or ""),
        "blocked_reasons": [
            reason for reason in [
                "quarantined_unknown_domain" if quarantined else "",
                "missing_url" if not url else "",
                "missing_retrieval_timestamp" if not record.get("retrieved_at") else "",
            ] if reason
        ],
    }


def build_promotion_template(root: Path, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = [evidence_candidate(record, idx + 1) for idx, record in enumerate(records)]
    template = {
        "version": VERSION,
        "created_at": now(),
        "instructions": [
            "This file is a review template. Nothing is promoted automatically.",
            "Set approved_for_promotion=true only after manually reviewing the URL/source.",
            "Add operator_notes for every approved item.",
            "Quarantined items should not be promoted unless a later trust-review build explicitly clears them.",
            "Promotion here writes only to reviewed web evidence store, not runtime truth.",
        ],
        "required_confirm_text": CONFIRM_TEXT,
        "operator_confirm_text": "",
        "runtime_truth_ingestion_enabled": False,
        "candidates": candidates,
    }
    write_json(root / PROMOTION_TEMPLATE_PATH, template)
    return template


def build_quarantine_queue(root: Path, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    queue = {
        "version": VERSION,
        "created_at": now(),
        "queue_type": "manual_quarantine_review",
        "may_feed_runtime_truth": False,
        "operator_review_required": True,
        "records": [evidence_candidate(record, idx + 1) for idx, record in enumerate(records)],
    }
    write_json(root / QUARANTINE_REVIEW_QUEUE_PATH, queue)
    return queue


def determine_status(live: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    warnings: List[str] = []

    if live["sources"]["last_result"].get("status") != "loaded" and live["sources"]["evidence_log"].get("status") != "loaded":
        warnings.append("no_live_probe_evidence_found_yet")
    if not live.get("last_result_executed", False):
        warnings.append("last_live_probe_not_executed_or_missing")
    if live.get("quarantine_count", 0):
        warnings.append(f"quarantined_records_present:{live['quarantine_count']}")
    if not template.get("candidates"):
        warnings.append("no_promotion_candidates_created")

    if blockers:
        status = "STOP"
        recommendation = "Fix blockers before evidence promotion review."
    elif warnings:
        status = "PROMOTION_REVIEW_READY_WITH_WARNINGS"
        recommendation = "Review evidence candidates. Do not promote quarantined or unreviewed records. Runtime truth ingestion remains disabled."
    else:
        status = "PROMOTION_REVIEW_READY"
        recommendation = "Evidence candidates are ready for manual review. Promotion requires explicit approval and confirmation."

    return {
        "status": status,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "recommendation": recommendation,
    }


def write_markdown(root: Path, gate: Dict[str, Any]) -> None:
    sg = gate["stop_go"]
    lines = [
        "# Claire v17.85 Governed Web Evidence Promotion Gate",
        "",
        f"Generated: {gate['generated_at']}",
        "",
        f"Status: **{sg['status']}**",
        "",
        f"Recommendation: {sg['recommendation']}",
        "",
        "## Hard Rules",
        "",
        "- This build does not promote evidence automatically.",
        "- Promotion requires manual review and confirm text.",
        "- Promotion writes to reviewed web evidence store only.",
        "- Runtime truth ingestion remains disabled.",
        "- Quarantined records remain in quarantine review.",
        "- Automatic updates and agent execution remain disabled.",
        "",
        "## Files",
        "",
        f"- `{PROMOTION_TEMPLATE_PATH}`",
        f"- `{QUARANTINE_REVIEW_QUEUE_PATH}`",
        f"- `{PROMOTED_STORE_PATH}`",
        "",
        "## Required confirm text",
        "",
        f"`{CONFIRM_TEXT}`",
        "",
        "## Counts",
        "",
        f"- Evidence candidates: {gate['candidate_count']}",
        f"- Quarantine records: {gate['quarantine_count']}",
        "",
    ]
    if sg["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for item in sg["warnings"]:
            lines.append(f"- {item}")
        lines.append("")
    if sg["blockers"]:
        lines.append("## Blockers")
        lines.append("")
        for item in sg["blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend([
        "## Swagger promotion endpoint",
        "",
        "POST `/internet/evidence-promotion/promote-approved`",
        "",
        "```json",
        json.dumps({"confirm_text": CONFIRM_TEXT}, indent=2),
        "```",
    ])
    write_text(root / STOP_GO_MD_PATH, "\n".join(lines))


def build_evidence_promotion_gate(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    live = load_live_probe_records(root)
    template = build_promotion_template(root, live["records"])
    quarantine_queue = build_quarantine_queue(root, live["quarantine_records"])
    stop_go = determine_status(live, template)

    provider_gate, provider_source = read_json(root / PROVIDER_GATE_PATH)
    allowlist, allowlist_source = read_json(root / ALLOWLIST_PATH)
    quarantine_policy, quarantine_policy_source = read_json(root / QUARANTINE_POLICY_PATH)

    gate = {
        "version": VERSION,
        "contract_name": CONTRACT_NAME,
        "generated_at": now(),
        "status": stop_go["status"],
        "stop_go": stop_go,
        "candidate_count": len(template.get("candidates", [])),
        "quarantine_count": len(quarantine_queue.get("records", [])),
        "live_probe_sources": live["sources"],
        "provider_gate_source": provider_source,
        "allowlist_source": allowlist_source,
        "quarantine_policy_source": quarantine_policy_source,
        "promotion_template_path": str(PROMOTION_TEMPLATE_PATH).replace("\\", "/"),
        "quarantine_queue_path": str(QUARANTINE_REVIEW_QUEUE_PATH).replace("\\", "/"),
        "promoted_store_path": str(PROMOTED_STORE_PATH).replace("\\", "/"),
        "governance": GOVERNANCE,
        "execution_defaults": {
            "promotion_runs_on_install": False,
            "automatic_promotion_enabled": False,
            "runtime_truth_ingestion_enabled": False,
            "automatic_updates_enabled": False,
            "agent_execution_enabled": False,
        },
        "next": [
            "Manually review promoted_evidence_candidates_template.json",
            "Set approved_for_promotion=true and operator_notes for approved non-quarantined records",
            "Use POST /internet/evidence-promotion/promote-approved with confirm text",
            "Later build: reviewed evidence to runtime truth gate",
        ],
    }

    write_json(root / PROMOTION_GATE_PATH, gate)
    write_json(root / STOP_GO_PATH, {"version": VERSION, "generated_at": gate["generated_at"], **stop_go})
    write_markdown(root, gate)

    dashboard_payload = {
        "version": VERSION,
        "generated_at": gate["generated_at"],
        "status": gate["status"],
        "recommendation": stop_go["recommendation"],
        "candidate_count": gate["candidate_count"],
        "quarantine_count": gate["quarantine_count"],
        "promotion_runs_on_install": False,
        "runtime_truth_ingestion_enabled": False,
        "automatic_promotion_enabled": False,
    }
    write_json(root / DASHBOARD_PAYLOAD_PATH, dashboard_payload)
    return gate


def load_promotion_template(root: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return read_json(root / PROMOTION_TEMPLATE_PATH)


def promote_approved_evidence(project_root: Optional[Path | str] = None, confirm_text: str = "") -> Dict[str, Any]:
    root = Path(project_root or Path.cwd()).resolve()
    gate = build_evidence_promotion_gate(root)

    if confirm_text != CONFIRM_TEXT:
        report = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "confirm_text_missing_or_wrong",
            "required_confirm_text": CONFIRM_TEXT,
            "promoted_count": 0,
            "runtime_truth_ingestion_enabled": False,
        }
        write_json(root / PROMOTION_EXECUTION_REPORT_PATH, report)
        return report

    template, source = load_promotion_template(root)
    if source.get("status") != "loaded":
        report = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "promotion_template_missing",
            "source": source,
            "promoted_count": 0,
            "runtime_truth_ingestion_enabled": False,
        }
        write_json(root / PROMOTION_EXECUTION_REPORT_PATH, report)
        return report

    if template.get("operator_confirm_text") != CONFIRM_TEXT:
        report = {
            "version": VERSION,
            "generated_at": now(),
            "status": "blocked",
            "executed": False,
            "reason": "template_operator_confirm_text_missing_or_wrong",
            "promoted_count": 0,
            "runtime_truth_ingestion_enabled": False,
        }
        write_json(root / PROMOTION_EXECUTION_REPORT_PATH, report)
        return report

    approved: List[Dict[str, Any]] = []
    blocked: List[Dict[str, Any]] = []
    for item in template.get("candidates", []):
        if not isinstance(item, dict) or item.get("approved_for_promotion") is not True:
            continue
        reasons = []
        if item.get("quarantined"):
            reasons.append("candidate_is_quarantined")
        if not item.get("url"):
            reasons.append("missing_url")
        if not item.get("retrieved_at"):
            reasons.append("missing_retrieval_timestamp")
        if not str(item.get("operator_notes") or "").strip():
            reasons.append("operator_notes_required")
        if reasons:
            blocked.append({"candidate_id": item.get("candidate_id"), "url": item.get("url"), "reasons": reasons})
            continue

        approved.append({
            "promoted_at": now(),
            "candidate_id": item.get("candidate_id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "source_domain": item.get("source_domain"),
            "snippet": item.get("snippet"),
            "retrieved_at": item.get("retrieved_at"),
            "provider": item.get("provider"),
            "query": item.get("query"),
            "trust_status": item.get("trust_status"),
            "operator_notes": item.get("operator_notes"),
            "may_feed_runtime_truth": False,
            "requires_later_runtime_truth_gate": True,
        })

    store = append_records(root / PROMOTED_STORE_PATH, approved, {
        "runtime_truth_ingestion_enabled": False,
        "promotion_gate_version": VERSION,
    })

    status = "promoted_with_blockers" if approved and blocked else "promoted" if approved else "blocked"
    reason = "approved_evidence_promoted_to_reviewed_store" if approved else "no_approved_records_promoted"

    report = {
        "version": VERSION,
        "generated_at": now(),
        "status": status,
        "executed": bool(approved),
        "reason": reason,
        "promoted_count": len(approved),
        "blocked_count": len(blocked),
        "blocked": blocked,
        "promoted_store_path": str(PROMOTED_STORE_PATH).replace("\\", "/"),
        "runtime_truth_ingestion_enabled": False,
        "automatic_updates_enabled": False,
        "agent_execution_enabled": False,
    }
    write_json(root / PROMOTION_EXECUTION_REPORT_PATH, report)
    return report


def evidence_promotion_summary(project_root: Optional[Path | str] = None) -> Dict[str, Any]:
    gate = build_evidence_promotion_gate(project_root)
    execution, execution_source = read_json(Path(project_root or Path.cwd()) / PROMOTION_EXECUTION_REPORT_PATH)
    return {
        "version": VERSION,
        "generated_at": now(),
        "status": gate.get("status"),
        "recommendation": gate.get("stop_go", {}).get("recommendation"),
        "candidate_count": gate.get("candidate_count"),
        "quarantine_count": gate.get("quarantine_count"),
        "promotion_template_path": gate.get("promotion_template_path"),
        "last_execution_source": execution_source,
        "last_execution_status": execution.get("status", "none"),
        "runtime_truth_ingestion_enabled": False,
        "automatic_promotion_enabled": False,
    }
