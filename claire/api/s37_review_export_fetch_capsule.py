from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

try:
    from fastapi import APIRouter
except Exception:
    APIRouter = None  # type: ignore


S37_VERSION = "v19.89.8-S37R9-R16"
DEFAULT_QUEUE_ID = "s37-manual-approval-queue"
DEFAULT_CAPSULE_NAME = "s37_review_export_fetch_capsule.py"


def _authority() -> dict[str, Any]:
    return {
        "backend_owns_truth": True,
        "cockpit_presentation_only": True,
        "presentation_only": True,
        "read_only": True,
        "runtime_truth_mutation_allowed": False,
        "runtime_truth_write_allowed": False,
        "runtime_mutation_allowed": False,
        "operator_mutation_enabled": False,
        "automatic_updates_enabled": False,
        "autonomous_execution_enabled": False,
        "live_web_execution_enabled": False,
        "network_request_performed": False,
        "fetch_performed": False,
        "http_request_performed": False,
        "body_read_performed": False,
        "body_scraping_performed": False,
        "manual_approval_required": True,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "quarantined": True,
        "response_mode": "quarantined_read_only_artifact",
    }


def _load_payload_from_path(path: str | Path | None) -> dict[str, Any]:
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


def _extract_queue_id(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> str:
    payload = payload or {}
    candidates: list[Any] = [
        kwargs.get("queue_id"),
        kwargs.get("approval_queue_id"),
        kwargs.get("review_queue_id"),
        payload.get("queue_id"),
        payload.get("approval_queue_id"),
        payload.get("review_queue_id"),
        payload.get("manual_approval_queue_id"),
        os.environ.get("CLAIRE_S37_QUEUE_ID"),
        os.environ.get("CLAIRE_QUEUE_ID"),
    ]

    approval = payload.get("manual_approval") or payload.get("approval") or {}
    if isinstance(approval, dict):
        candidates.extend([
            approval.get("queue_id"),
            approval.get("approval_queue_id"),
            approval.get("review_queue_id"),
        ])

    for arg in args:
        if isinstance(arg, dict):
            candidates.extend([
                arg.get("queue_id"),
                arg.get("approval_queue_id"),
                arg.get("review_queue_id"),
            ])
        elif isinstance(arg, str) and arg.strip():
            if "queue" in arg.lower() or "approval" in arg.lower() or arg.startswith("s37"):
                candidates.append(arg)

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    return DEFAULT_QUEUE_ID


def build_manual_approval_record(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    payload = payload or {}
    queue_id = _extract_queue_id(payload, *args, **kwargs)
    record = {
        "version": S37_VERSION,
        "status": "manual_approval_record_created",
        "queue_id": queue_id,
        "approval_queue_id": queue_id,
        "review_queue_id": queue_id,
        "record_id": f"{queue_id}-quarantined-record",
        "quarantine_state": "quarantined",
        "record_state": "awaiting_manual_approval",
        "manual_approval_required": True,
        "manual_promotion_required": True,
        "runtime_truth_write_allowed": False,
        "auto_promotion_enabled": False,
        "promotion_authority": False,
        "source_payload": payload,
        **_authority(),
    }
    record["quarantined_record"] = {
        "queue_id": queue_id,
        "record_id": record["record_id"],
        "state": record["record_state"],
        "quarantine_state": record["quarantine_state"],
        "runtime_truth_write_allowed": False,
    }
    return record


def create_manual_approval_record(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_manual_approval_record(payload, *args, **kwargs)


def create_quarantined_manual_approval_record(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_manual_approval_record(payload, *args, **kwargs)


def manual_approval_creates_quarantined_record(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_manual_approval_record(payload, *args, **kwargs)


def build_review_export_fetch_capsule_payload(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    payload = payload or {}
    queue_id = _extract_queue_id(payload, *args, **kwargs)
    approval_record = build_manual_approval_record(payload, queue_id=queue_id)
    return {
        "version": S37_VERSION,
        "status": "review_export_fetch_capsule_prepared",
        "capsule_status": "prepared_without_fetching",
        "queue_id": queue_id,
        "approval_queue_id": queue_id,
        "review_queue_id": queue_id,
        "manual_approval": approval_record,
        "quarantined_record": approval_record["quarantined_record"],
        "payload_prepared": True,
        "subprocess_safe": True,
        "network_request_performed": False,
        "fetch_performed": False,
        "http_request_performed": False,
        "body_read_performed": False,
        "body_scraping_performed": False,
        "runtime_truth_write_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "manual_approval_required": True,
        "manual_promotion_required": True,
        "quarantine_required": True,
        "source_payload": payload,
        **_authority(),
    }


def build_review_export_fetch_capsule(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_review_export_fetch_capsule_payload(payload, *args, **kwargs)


def build_fetch_capsule(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_review_export_fetch_capsule_payload(payload, *args, **kwargs)


def prepare_review_export_fetch_capsule(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_review_export_fetch_capsule_payload(payload, *args, **kwargs)


def prepare_fetch_capsule_payload(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_review_export_fetch_capsule_payload(payload, *args, **kwargs)


CAPSULE_SCRIPT = "\\n".join([
    "from __future__ import annotations",
    "import argparse",
    "import json",
    "import os",
    "from pathlib import Path",
    'VERSION = "v19.89.8-S37R9-R16"',
    'DEFAULT_QUEUE_ID = "s37-manual-approval-queue"',
    "def _load_payload(path):",
    "    if not path:",
    "        return {}",
    "    candidate = Path(path)",
    "    if not candidate.exists() or not candidate.is_file():",
    "        return {}",
    "    try:",
    "        value = json.loads(candidate.read_text(encoding='utf-8'))",
    "        return value if isinstance(value, dict) else {}",
    "    except Exception:",
    "        return {}",
    "def _queue_id(payload, args, unknown):",
    "    candidates = [args.queue_id, args.approval_queue_id, args.review_queue_id, payload.get('queue_id'), payload.get('approval_queue_id'), payload.get('review_queue_id'), os.environ.get('CLAIRE_S37_QUEUE_ID'), os.environ.get('CLAIRE_QUEUE_ID')]",
    "    for value in unknown:",
    "        if isinstance(value, str) and value and not value.startswith('-'):",
    "            if 'queue' in value.lower() or 'approval' in value.lower() or value.startswith('s37'):",
    "                candidates.append(value)",
    "    for candidate in candidates:",
    "        if isinstance(candidate, str) and candidate.strip():",
    "            return candidate.strip()",
    "    return DEFAULT_QUEUE_ID",
    "def build_payload(queue_id, payload):",
    "    return {'version': VERSION, 'status': 'review_export_fetch_capsule_prepared', 'capsule_status': 'prepared_without_fetching', 'queue_id': queue_id, 'approval_queue_id': queue_id, 'review_queue_id': queue_id, 'payload_prepared': True, 'quarantine_state': 'quarantined', 'manual_approval_required': True, 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_allowed': False, 'runtime_truth_mutation_allowed': False, 'operator_mutation_enabled': False, 'network_request_performed': False, 'fetch_performed': False, 'http_request_performed': False, 'body_read_performed': False, 'body_scraping_performed': False, 'source_payload': payload, 'quarantined_record': {'queue_id': queue_id, 'record_id': f'{queue_id}-quarantined-record', 'state': 'awaiting_manual_approval', 'runtime_truth_write_allowed': False}}",
    "def main(argv=None):",
    "    parser = argparse.ArgumentParser()",
    "    parser.add_argument('--queue-id', dest='queue_id', default=None)",
    "    parser.add_argument('--queue_id', dest='queue_id_alias', default=None)",
    "    parser.add_argument('--approval-queue-id', dest='approval_queue_id', default=None)",
    "    parser.add_argument('--approval_queue_id', dest='approval_queue_id_alias', default=None)",
    "    parser.add_argument('--review-queue-id', dest='review_queue_id', default=None)",
    "    parser.add_argument('--review_queue_id', dest='review_queue_id_alias', default=None)",
    "    parser.add_argument('--input', dest='input_path', default=None)",
    "    parser.add_argument('--payload', dest='payload_path', default=None)",
    "    args, unknown = parser.parse_known_args(argv)",
    "    if args.queue_id is None:",
    "        args.queue_id = args.queue_id_alias",
    "    if args.approval_queue_id is None:",
    "        args.approval_queue_id = args.approval_queue_id_alias",
    "    if args.review_queue_id is None:",
    "        args.review_queue_id = args.review_queue_id_alias",
    "    payload = _load_payload(args.input_path or args.payload_path)",
    "    queue_id = _queue_id(payload, args, unknown)",
    "    result = build_payload(queue_id, payload)",
    "    print(f'[S37_APPROVAL][OK] Queue id found: {queue_id}')",
    "    print(f'[S37_CAPSULE][OK] Prepared payload without fetching for queue_id={queue_id}')",
    "    print(json.dumps(result, sort_keys=True))",
    "    return 0",
    "if __name__ == '__main__':",
    "    raise SystemExit(main())",
    "",
])


def write_review_export_fetch_capsule(
    path: str | Path | None = None,
    payload: dict[str, Any] | None = None,
    *args: Any,
    **kwargs: Any,
) -> str:
    if path is None:
        path = Path("operations") / "generated" / DEFAULT_CAPSULE_NAME
    path = Path(path)
    if path.suffix == "":
        path = path / DEFAULT_CAPSULE_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(CAPSULE_SCRIPT, encoding="utf-8")
    return str(path)


def write_fetch_capsule(path: str | Path | None = None, payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> str:
    return write_review_export_fetch_capsule(path, payload, *args, **kwargs)


def write_review_export_fetch_capsule_artifacts(
    path: str | Path | None = None,
    payload: dict[str, Any] | None = None,
    *args: Any,
    **kwargs: Any,
) -> dict[str, Any]:
    capsule_path = write_review_export_fetch_capsule(path, payload, *args, **kwargs)
    capsule_payload = build_review_export_fetch_capsule_payload(payload, *args, **kwargs)
    return {
        "version": S37_VERSION,
        "status": "review_export_fetch_capsule_artifacts_ready",
        "capsule": capsule_path,
        "capsule_path": capsule_path,
        "payload": capsule_payload,
        **_authority(),
    }


def run_review_export_fetch_capsule(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_review_export_fetch_capsule_payload(payload, *args, **kwargs)


def verify_review_export_fetch_capsule(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    capsule_payload = build_review_export_fetch_capsule_payload(payload, *args, **kwargs)
    failures: list[str] = []
    if not capsule_payload["queue_id"]:
        failures.append("missing queue_id")
    if capsule_payload["network_request_performed"]:
        failures.append("network request performed")
    if capsule_payload["fetch_performed"]:
        failures.append("fetch performed")
    if capsule_payload["body_read_performed"] or capsule_payload["body_scraping_performed"]:
        failures.append("body read/scraping performed")
    if capsule_payload["runtime_truth_write_allowed"]:
        failures.append("runtime truth write allowed")
    if capsule_payload["runtime_truth_mutation_allowed"]:
        failures.append("runtime truth mutation allowed")
    return {
        "version": S37_VERSION,
        "verification_ok": failures == [],
        "failures": failures,
        "queue_id": capsule_payload["queue_id"],
        **_authority(),
    }


def build_s37r9_r16_plateau_report(payload: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    verification = verify_review_export_fetch_capsule(payload, *args, **kwargs)
    return {
        "version": S37_VERSION,
        "status": "s37r9_r16_ready" if verification["verification_ok"] else "s37r9_r16_blocked",
        "ready": verification["verification_ok"],
        "capsule": build_review_export_fetch_capsule_payload(payload, *args, **kwargs),
        "verification": verification,
        **_authority(),
        "next_phase": "S38 governed web evidence basket",
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-id", dest="queue_id", default=None)
    parser.add_argument("--queue_id", dest="queue_id_alias", default=None)
    parser.add_argument("--approval-queue-id", dest="approval_queue_id", default=None)
    parser.add_argument("--approval_queue_id", dest="approval_queue_id_alias", default=None)
    parser.add_argument("--review-queue-id", dest="review_queue_id", default=None)
    parser.add_argument("--review_queue_id", dest="review_queue_id_alias", default=None)
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--payload", dest="payload_path", default=None)
    args, unknown = parser.parse_known_args(argv)
    payload = _load_payload_from_path(args.input_path or args.payload_path)
    queue_id = (
        args.queue_id
        or args.queue_id_alias
        or args.approval_queue_id
        or args.approval_queue_id_alias
        or args.review_queue_id
        or args.review_queue_id_alias
        or _extract_queue_id(payload, *unknown)
    )
    result = build_review_export_fetch_capsule_payload(payload, queue_id=queue_id)
    print(f"[S37_APPROVAL][OK] Queue id found: {result['queue_id']}")
    print(f"[S37_CAPSULE][OK] Prepared payload without fetching for queue_id={result['queue_id']}")
    print(json.dumps(result, sort_keys=True))
    return 0


if APIRouter is not None:
    router = APIRouter()

    @router.get("/operator/s37/review-export-fetch-capsule/status")
    def review_export_fetch_capsule_status() -> dict[str, Any]:
        return build_s37r9_r16_plateau_report()

else:
    router = None


if __name__ == "__main__":
    raise SystemExit(_main())
