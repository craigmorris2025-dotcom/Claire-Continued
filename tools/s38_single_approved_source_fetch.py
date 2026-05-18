from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNTIME_DIR = ROOT / "runtime" / "governed_web_fetch"
SOURCE_PLAN = ROOT / "runtime" / "governed_system_inventory" / "s37_approved_source_fetch_plan.json"
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_web_evidence"
FETCH_MANIFEST = RUNTIME_DIR / "s38_last_single_fetch_manifest.json"


MAX_BYTES = 65536


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _domain_allowed(url: str, allowed_domains: list[str]) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in allowed_domains)


def _load_plan() -> dict:
    if not SOURCE_PLAN.exists():
        raise RuntimeError("S37 approved source fetch plan missing.")
    return json.loads(SOURCE_PLAN.read_text(encoding="utf-8"))


def _fetch_limited_text(url: str) -> dict:
    request = Request(
        url,
        headers={"User-Agent": "Claire-Syntalion-Governed-Approved-Source-Fetch/1.0"},
        method="GET",
    )
    start = time.perf_counter()
    context = ssl.create_default_context()
    with urlopen(request, timeout=10, context=context) as response:
        status = getattr(response, "status", None)
        headers = dict(response.headers.items())
        content_type = headers.get("Content-Type") or headers.get("content-type")
        body = response.read(MAX_BYTES + 1)
    truncated = len(body) > MAX_BYTES
    body = body[:MAX_BYTES]
    latency_ms = round((time.perf_counter() - start) * 1000, 3)
    text_preview = body.decode("utf-8", errors="replace")
    return {
        "status": status,
        "headers": headers,
        "content_type": content_type,
        "latency_ms": latency_ms,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "body_bytes_captured": len(body),
        "body_truncated": truncated,
        "text_preview": text_preview[:5000],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one governed approved-source fetch and quarantine evidence.")
    parser.add_argument("--operator-ack", required=True, choices=["YES"])
    parser.add_argument("--approval-id", required=True)
    args = parser.parse_args()

    plan = _load_plan()
    if plan.get("approval_id") != args.approval_id:
        print("[S38-FETCH][BLOCKED] Approval id does not match active S37 fetch plan.")
        return 1
    if plan.get("ready_for_s38_single_fetch") is not True:
        print("[S38-FETCH][BLOCKED] S37 plan is not ready for S38 single fetch.")
        return 1

    url = plan.get("candidate_url")
    allowed_domains = plan.get("allowed_domains", [])
    if not url or not _domain_allowed(url, allowed_domains):
        print("[S38-FETCH][BLOCKED] Candidate URL is not allowed by source policy.")
        return 1

    fetched = _fetch_limited_text(url)

    record = {
        "version": "v19.89.8-S38R1-R4-first-approved-source-fetch",
        "fetched_at": _utc_now(),
        "approval_id": args.approval_id,
        "queue_id": plan.get("queue_id"),
        "url": url,
        "allowed_domains": allowed_domains,
        "source_policy_passed": True,
        "single_fetch_only": True,
        "browser_execution": False,
        "javascript_execution": False,
        "autonomous_execution": False,
        "runtime_truth_mutation": False,
        "automatic_update_applied": False,
        "manual_promotion_required": True,
        "quarantined": True,
        "max_bytes": MAX_BYTES,
        "evidence": fetched,
    }

    safe = str(int(time.time() * 1000))
    quarantine_path = QUARANTINE_DIR / f"s38_approved_source_evidence_{safe}.json"
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    quarantine_path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")

    manifest = {
        "version": record["version"],
        "completed_at": record["fetched_at"],
        "approval_id": args.approval_id,
        "url": url,
        "quarantine_path": str(quarantine_path),
        "status": fetched.get("status"),
        "content_type": fetched.get("content_type"),
        "body_sha256": fetched.get("body_sha256"),
        "manual_promotion_required": True,
        "runtime_truth_mutation": False,
        "automatic_update_applied": False,
    }
    FETCH_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("[S38-FETCH] PASS")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
