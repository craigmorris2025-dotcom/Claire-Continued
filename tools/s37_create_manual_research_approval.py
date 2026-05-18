from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


VERSION = "v19.89.8-S37R9-R16"
DEFAULT_QUEUE_ID = "s37-manual-approval-queue"


def _load_payload(path: str | None) -> dict:
    if not path:
        return {}
    candidate = Path(path)
    if not candidate.exists() or not candidate.is_file():
        return {}
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _first_text(*values) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _queue_id(args: argparse.Namespace, payload: dict, unknown: list[str]) -> str:
    approval = payload.get("manual_approval") or payload.get("approval") or {}
    if not isinstance(approval, dict):
        approval = {}

    candidates = [
        args.queue_id,
        args.queue_id_alias,
        args.approval_queue_id,
        args.approval_queue_id_alias,
        args.review_queue_id,
        args.review_queue_id_alias,
        payload.get("queue_id"),
        payload.get("approval_queue_id"),
        payload.get("review_queue_id"),
        payload.get("manual_approval_queue_id"),
        approval.get("queue_id"),
        approval.get("approval_queue_id"),
        approval.get("review_queue_id"),
        os.environ.get("CLAIRE_S37_QUEUE_ID"),
        os.environ.get("CLAIRE_QUEUE_ID"),
    ]

    for value in unknown:
        if isinstance(value, str) and value and not value.startswith("-"):
            if "queue" in value.lower() or "approval" in value.lower() or value.startswith("S37") or value.startswith("s37"):
                candidates.append(value)

    return _first_text(*candidates) or DEFAULT_QUEUE_ID


def build_manual_approval_record(queue_id: str, candidate_url: str | None, operator_ack: str | None, payload: dict) -> dict:
    return {
        "version": VERSION,
        "status": "manual_approval_record_created",
        "queue_id": queue_id,
        "approval_queue_id": queue_id,
        "review_queue_id": queue_id,
        "candidate_url": candidate_url,
        "operator_ack": operator_ack,
        "operator_acknowledged": str(operator_ack).upper() in {"YES", "Y", "TRUE", "1"},
        "record_id": f"{queue_id}-quarantined-record",
        "record_state": "awaiting_manual_review",
        "quarantine_state": "quarantined",
        "quarantined_record_created": True,
        "manual_approval_required": True,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "runtime_truth_write_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "fetch_performed": False,
        "http_request_performed": False,
        "body_read_performed": False,
        "body_scraping_performed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_payload": payload,
        "quarantined_record": {
            "queue_id": queue_id,
            "record_id": f"{queue_id}-quarantined-record",
            "state": "awaiting_manual_review",
            "quarantine_state": "quarantined",
            "runtime_truth_write_allowed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a quarantined S37 manual research approval record.")
    parser.add_argument("--queue-id", dest="queue_id", default=None)
    parser.add_argument("--queue_id", dest="queue_id_alias", default=None)
    parser.add_argument("--approval-queue-id", dest="approval_queue_id", default=None)
    parser.add_argument("--approval_queue_id", dest="approval_queue_id_alias", default=None)
    parser.add_argument("--review-queue-id", dest="review_queue_id", default=None)
    parser.add_argument("--review_queue_id", dest="review_queue_id_alias", default=None)
    parser.add_argument("--candidate-url", dest="candidate_url", default=None)
    parser.add_argument("--candidate_url", dest="candidate_url_alias", default=None)
    parser.add_argument("--operator-ack", dest="operator_ack", default=None)
    parser.add_argument("--operator_ack", dest="operator_ack_alias", default=None)
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--payload", dest="payload_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)

    args, unknown = parser.parse_known_args(argv)
    payload = _load_payload(args.input_path or args.payload_path)
    queue_id = _queue_id(args, payload, unknown)
    candidate_url = _first_text(args.candidate_url, args.candidate_url_alias, payload.get("candidate_url"))
    operator_ack = _first_text(args.operator_ack, args.operator_ack_alias, payload.get("operator_ack"))

    record = build_manual_approval_record(queue_id, candidate_url, operator_ack, payload)

    if args.output_path:
        output_path = Path(args.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    print(f"[S37_APPROVAL][OK] Queue id found: {queue_id}")
    print(f"[S37_APPROVAL][OK] Quarantined record created for queue_id={queue_id}")
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
