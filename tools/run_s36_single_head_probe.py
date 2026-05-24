from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RUNTIME_DIR = ROOT / "runtime" / "governed_live_probe"
MANIFEST_PATH = RUNTIME_DIR / "operator_single_head_probe_request.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _enable_operator_gates() -> None:
    os.environ["PLATFORM_ALLOW_GOVERNED_LIVE_METADATA_PROBE"] = "1"
    os.environ["PLATFORM_ALLOW_HEAD_ONLY_PROBE"] = "1"

    # Explicitly force unsafe authorities off for this process.
    os.environ.pop("PLATFORM_ALLOW_RESPONSE_BODY_READ", None)
    os.environ.pop("PLATFORM_ALLOW_RUNTIME_TRUTH_MUTATION", None)
    os.environ.pop("PLATFORM_ALLOW_AUTONOMOUS_EXECUTION", None)


async def _run(url: str) -> dict:
    from runtime_core.api.routes.governed_live_probe import HeadProbeRequest, run_governed_head_probe

    _enable_operator_gates()
    payload = HeadProbeRequest(url=url, operator_ack=True, one_shot=True)
    result = await run_governed_head_probe(payload)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run exactly one governed HEAD-only metadata probe. No body read. No browser. No runtime mutation."
    )
    parser.add_argument("--url", required=True, help="http/https URL for one HEAD-only metadata probe")
    parser.add_argument(
        "--operator-ack",
        required=True,
        choices=["YES"],
        help="Must be YES to acknowledge one-shot operator-triggered execution.",
    )
    args = parser.parse_args()

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    request_manifest = {
        "version": "v19.89.8-S36R22.1-first-live-runner-bootstrap-fix",
        "requested_at": _utc_now(),
        "url": args.url,
        "operator_ack": True,
        "one_shot_only": True,
        "method": "HEAD",
        "body_read": False,
        "browser_execution": False,
        "runtime_truth_mutation": False,
        "autonomous_execution": False,
        "automatic_updates": False,
        "manual_promotion_required": True,
        "bootstrap_root": str(ROOT),
    }
    MANIFEST_PATH.write_text(json.dumps(request_manifest, indent=2, sort_keys=True), encoding="utf-8")

    result = asyncio.run(_run(args.url))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
