from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple


LEGACY_CONTINUOUS_RUNTIME_STATUS = "configured_not_running"


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_continuous_runtime_files(root: Optional[str | Path] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    base = Path(root) if root is not None else Path.cwd()

    data_runtime = base / "data" / "continuous_runtime"
    review_queue = base / "data" / "review_queue"
    output_runtime = base / "output" / "continuous_runtime"

    data_runtime.mkdir(parents=True, exist_ok=True)
    review_queue.mkdir(parents=True, exist_ok=True)
    output_runtime.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()

    status_payload = {
        "status": "success",
        "continuous_runtime_status": LEGACY_CONTINUOUS_RUNTIME_STATUS,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": False,
        "configured": True,
        "created_at": now,
    }

    candidate_payload = {
        "status": "success",
        "continuous_runtime_status": LEGACY_CONTINUOUS_RUNTIME_STATUS,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": True,
        "candidates": [],
        "created_at": now,
    }

    files = {
        "status_file": data_runtime / "status.json",
        "cycle_file": data_runtime / "cycle.json",
        "manifest_file": data_runtime / "manifest.json",
        "review_candidates_file": review_queue / "review_candidates.json",
        "output_status_file": output_runtime / "status.json",
    }

    _write_json(files["status_file"], status_payload)
    _write_json(files["cycle_file"], status_payload)
    _write_json(files["manifest_file"], status_payload)
    _write_json(files["review_candidates_file"], candidate_payload)
    _write_json(files["output_status_file"], status_payload)

    return {
        "status": "success",
        "success": True,
        "ok": True,
        "continuous_runtime_status": LEGACY_CONTINUOUS_RUNTIME_STATUS,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": False,
        "data_runtime_dir": str(data_runtime),
        "review_queue_dir": str(review_queue),
        **{key: str(value) for key, value in files.items()},
    }


def _looks_like_path(value: Any) -> bool:
    if isinstance(value, Path):
        return True
    text = str(value)
    return (
        text in {".", ".."}
        or "/" in text
        or "\\\\" in text
        or (len(text) >= 2 and text[1] == ":")
    )


def _coerce_args(*args: Any, **kwargs: Any) -> Tuple[Path, Dict[str, Any]]:
    root = Path.cwd()
    request: Dict[str, Any] = {}

    remaining = list(args)
    if remaining:
        first = remaining[0]
        if isinstance(first, (str, Path)) and _looks_like_path(first):
            root = Path(first)
            remaining = remaining[1:]

    for arg in remaining:
        if isinstance(arg, Mapping):
            request.update(dict(arg))
        elif isinstance(arg, str):
            request.setdefault("input_summary", arg)
        elif arg is not None:
            request.setdefault("extra_args", []).append(arg)

    for key in ["root", "base_dir", "project_root", "output_root"]:
        if key in kwargs:
            root = Path(kwargs.pop(key))

    request.update(kwargs)
    request.setdefault("input_summary", "continuous runtime compatibility cycle")
    return root, request


def run_once(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    root, request = _coerce_args(*args, **kwargs)
    files = ensure_continuous_runtime_files(root)

    candidate = {
        "candidate_id": "legacy_continuous_runtime_review_candidate",
        "status": "pending_review",
        "input_summary": request.get("input_summary", ""),
        "runtime_truth_mutated": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    review_file = Path(files["review_candidates_file"])
    _write_json(
        review_file,
        {
            "status": "success",
            "continuous_runtime_status": LEGACY_CONTINUOUS_RUNTIME_STATUS,
            "loop_running": False,
            "runtime_truth_mutated": False,
            "promotion_required": True,
            "review_candidate_created": True,
            "candidates": [candidate],
        },
    )

    return {
        "status": "success",
        "success": True,
        "ok": True,
        "continuous_runtime_status": LEGACY_CONTINUOUS_RUNTIME_STATUS,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": True,
        "candidate": candidate,
        "files": files,
    }


class ContinuousRuntimeCycle:
    def run(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return run_once(*args, **kwargs)


def ensure_continuous_runtime_cycle() -> ContinuousRuntimeCycle:
    return ContinuousRuntimeCycle()


def run_continuous_runtime_cycle(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return run_once(*args, **kwargs)


ensure_cycle = ensure_continuous_runtime_cycle
run_cycle = run_continuous_runtime_cycle
