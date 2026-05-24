
from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from runtime_core.live.live_ingestion_quarantine import ingest_live_candidate


QUEUE_STATE_PATH = Path("data/live/governed_async_ingestion_queue.json")


@dataclass
class LiveIngestionJob:
    source_url: str
    title: str
    payload: Dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 2
    timeout_seconds: float = 5.0


def _write_queue_state(records: List[Dict[str, Any]]) -> None:
    QUEUE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "16.64",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "job_count": len(records),
        "records": records,
    }
    QUEUE_STATE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


async def _run_job(job: LiveIngestionJob) -> Dict[str, Any]:
    attempts = 0
    last_error = None

    while attempts < job.max_attempts:
        attempts += 1
        try:
            await asyncio.sleep(0)
            result = ingest_live_candidate(job.source_url, job.title, job.payload)
            return {
                "status": "completed",
                "attempts": attempts,
                "job": asdict(job),
                "result": result,
            }
        except Exception as exc:
            last_error = str(exc)

    return {
        "status": "failed",
        "attempts": attempts,
        "job": asdict(job),
        "error": last_error,
    }


async def run_governed_ingestion_queue_async(jobs: List[LiveIngestionJob]) -> Dict[str, Any]:
    records = []

    for job in jobs:
        try:
            result = await asyncio.wait_for(_run_job(job), timeout=job.timeout_seconds)
        except Exception as exc:
            result = {
                "status": "timeout_or_error",
                "job": asdict(job),
                "error": str(exc),
            }
        records.append(result)

    _write_queue_state(records)

    return {
        "version": "16.64",
        "status": "completed",
        "job_count": len(records),
        "records": records,
    }


def run_governed_ingestion_queue(jobs: List[LiveIngestionJob]) -> Dict[str, Any]:
    return asyncio.run(run_governed_ingestion_queue_async(jobs))
