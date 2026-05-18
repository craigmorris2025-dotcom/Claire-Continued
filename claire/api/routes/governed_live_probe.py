from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/api/governed/live-probe",
    tags=["governed-live-probe"],
)

ROOT = Path.cwd()
QUARANTINE_DIR = ROOT / "data" / "quarantine" / "governed_live_metadata"
MANIFEST_DIR = ROOT / "runtime" / "governed_live_probe"

PROVIDER_GATE_ENV = "CLAIRE_ALLOW_GOVERNED_LIVE_METADATA_PROBE"
HEAD_GATE_ENV = "CLAIRE_ALLOW_HEAD_ONLY_PROBE"
BODY_READ_ENV = "CLAIRE_ALLOW_RESPONSE_BODY_READ"
RUNTIME_MUTATION_ENV = "CLAIRE_ALLOW_RUNTIME_TRUTH_MUTATION"
AUTONOMOUS_ENV = "CLAIRE_ALLOW_AUTONOMOUS_EXECUTION"


class HeadProbeRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)
    operator_ack: bool = Field(False)
    one_shot: bool = Field(True)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _gate_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _guarded_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"}:
        raise HTTPException(status_code=400, detail="Only http/https URLs are allowed for HEAD metadata probe.")
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL must include a network location.")
    return url


def _assert_execution_allowed(payload: HeadProbeRequest) -> None:
    if not payload.operator_ack:
        raise HTTPException(status_code=403, detail="Operator acknowledgement required.")
    if not payload.one_shot:
        raise HTTPException(status_code=403, detail="Only one-shot execution is allowed.")
    if not _gate_enabled(PROVIDER_GATE_ENV):
        raise HTTPException(status_code=403, detail="Governed live metadata provider gate is disabled.")
    if not _gate_enabled(HEAD_GATE_ENV):
        raise HTTPException(status_code=403, detail="HEAD-only probe gate is disabled.")
    if _gate_enabled(BODY_READ_ENV):
        raise HTTPException(status_code=403, detail="Body-read authority must remain disabled.")
    if _gate_enabled(RUNTIME_MUTATION_ENV):
        raise HTTPException(status_code=403, detail="Runtime truth mutation must remain disabled.")
    if _gate_enabled(AUTONOMOUS_ENV):
        raise HTTPException(status_code=403, detail="Autonomous execution must remain disabled.")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


async def _head_metadata_only(url: str) -> dict[str, Any]:
    import http.client

    parsed = urlparse(url)
    conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    host = parsed.netloc
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    start = time.perf_counter()

    def do_request() -> dict[str, Any]:
        conn = conn_cls(host, timeout=10)
        try:
            conn.request("HEAD", path, headers={"User-Agent": "Claire-Syntalion-Governed-Metadata-Probe/1.0"})
            response = conn.getresponse()
            headers = {k.lower(): v for k, v in response.getheaders()}
            return {
                "status": response.status,
                "reason": response.reason,
                "headers": headers,
                "content_type": headers.get("content-type"),
            }
        finally:
            conn.close()

    result = await asyncio.to_thread(do_request)
    result["latency_ms"] = round((time.perf_counter() - start) * 1000, 3)
    return result


@router.get("/status")
def governed_live_probe_status() -> dict[str, Any]:
    return {
        "version": "v19.89.8-S36R1D-router-only-exclude-bridge",
        "registered": True,
        "operator_triggered_only": True,
        "one_shot_only": True,
        "method_allowed": "HEAD",
        "body_reads_allowed": False,
        "browser_execution_allowed": False,
        "runtime_truth_mutation_allowed": False,
        "autonomous_execution_allowed": False,
        "provider_gate_enabled": _gate_enabled(PROVIDER_GATE_ENV),
        "head_gate_enabled": _gate_enabled(HEAD_GATE_ENV),
        "quarantine_dir": str(QUARANTINE_DIR),
        "updated_at": _utc_now(),
    }


@router.post("/head")
async def run_governed_head_probe(payload: HeadProbeRequest) -> dict[str, Any]:
    _assert_execution_allowed(payload)
    url = _guarded_url(payload.url)
    metadata = await _head_metadata_only(url)

    record = {
        "version": "v19.89.8-S36R1D-router-only-exclude-bridge",
        "probe_type": "HEAD_METADATA_ONLY",
        "url": url,
        "completed_at": _utc_now(),
        "operator_triggered_only": True,
        "one_shot_only": True,
        "body_read": False,
        "browser_execution": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "metadata": metadata,
        "manual_promotion_required": True,
        "quarantined": True,
    }

    safe_name = str(int(time.time() * 1000))
    quarantine_path = QUARANTINE_DIR / f"head_probe_{safe_name}.json"
    manifest_path = MANIFEST_DIR / "last_single_head_probe_manifest.json"

    _write_json(quarantine_path, record)
    _write_json(manifest_path, {
        "last_probe_quarantine_path": str(quarantine_path),
        "completed_at": record["completed_at"],
        "status": metadata.get("status"),
        "body_read": False,
        "manual_promotion_required": True,
    })

    return {
        "ok": True,
        "quarantined": True,
        "quarantine_path": str(quarantine_path),
        "manual_promotion_required": True,
        "metadata_only": True,
        "body_read": False,
        "status": metadata.get("status"),
        "content_type": metadata.get("content_type"),
        "latency_ms": metadata.get("latency_ms"),
    }
