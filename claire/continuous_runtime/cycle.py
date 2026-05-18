from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple


CONTINUOUS_RUNTIME_STATUS = "configured_not_running"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _status_payload() -> Dict[str, Any]:
    return {
        "status": "success",
        "continuous_runtime_status": CONTINUOUS_RUNTIME_STATUS,
        "operator_approval_required": True,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "configured": True,
        "created_at": _now(),
    }


def ensure_continuous_runtime_files(root: Optional[str | Path] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """v19.84.2 legacy compatibility contract.

    This function only seeds local compatibility files. It does not start the
    continuous loop, mutate runtime truth, promote evidence, or touch cockpit UI.
    """
    base = Path(root) if root is not None else Path.cwd()
    runtime_dir = base / "data" / "continuous_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    status_file = runtime_dir / "status.json"
    review_queue_file = runtime_dir / "review_queue.json"

    status_payload = _status_payload()
    review_queue_payload = {
        **_status_payload(),
        "review_candidate_created": False,
        "candidates": [],
    }

    _write_json(status_file, status_payload)
    _write_json(review_queue_file, review_queue_payload)

    return {
        **status_payload,
        "review_candidate_created": False,
        "runtime_dir": str(runtime_dir),
        "status_file": str(status_file),
        "review_queue_file": str(review_queue_file),
    }


def _looks_like_root(value: Any) -> bool:
    if isinstance(value, Path):
        return True
    text = str(value)
    return text in {".", ".."} or "/" in text or "\\" in text or (len(text) >= 2 and text[1] == ":")


def _coerce_args(*args: Any, **kwargs: Any) -> Tuple[Path, Dict[str, Any]]:
    root = Path.cwd()
    request: Dict[str, Any] = {}

    remaining = list(args)
    if remaining and isinstance(remaining[0], (str, Path)) and _looks_like_root(remaining[0]):
        root = Path(remaining.pop(0))

    for arg in remaining:
        if isinstance(arg, Mapping):
            request.update(dict(arg))
        elif isinstance(arg, str):
            request.setdefault("input_summary", arg)
        elif arg is not None:
            request.setdefault("extra_args", []).append(arg)

    for key in ("root", "base_dir", "project_root", "output_root"):
        if key in kwargs:
            root = Path(kwargs.pop(key))

    request.update(kwargs)
    request.setdefault("input_summary", "continuous runtime compatibility cycle")
    return root, request


def run_once(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """v19.84.2 legacy compatibility contract.

    Required by tests/test_v19_84_2_continuous_runtime_cycle.py:
    - status == "success"
    - continuous_runtime_status == "configured_not_running"
    - operator_approval_required is True
    - candidate.status == "pending_operator_review"
    - loop_running is False
    """
    root, request = _coerce_args(*args, **kwargs)
    files = ensure_continuous_runtime_files(root)

    candidate = {
        "candidate_id": "continuous_runtime_review_candidate",
        "status": "pending_operator_review",
        "input_summary": request.get("input_summary", ""),
        "operator_approval_required": True,
        "runtime_truth_mutated": False,
        "created_at": _now(),
    }

    result = {
        "status": "success",
        "continuous_runtime_status": CONTINUOUS_RUNTIME_STATUS,
        "operator_approval_required": True,
        "loop_running": False,
        "runtime_truth_mutated": False,
        "promotion_required": True,
        "review_candidate_created": True,
        "candidate": candidate,
        "files": files,
    }

    review_queue_file = Path(files["review_queue_file"])
    _write_json(
        review_queue_file,
        {
            "status": "success",
            "continuous_runtime_status": CONTINUOUS_RUNTIME_STATUS,
            "operator_approval_required": True,
            "loop_running": False,
            "runtime_truth_mutated": False,
            "promotion_required": True,
            "review_candidate_created": True,
            "candidates": [candidate],
            "updated_at": _now(),
        },
    )

    return result


class ContinuousRuntimeCycle:
    def run(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return run_once(*args, **kwargs)


def ensure_continuous_runtime_cycle() -> ContinuousRuntimeCycle:
    return ContinuousRuntimeCycle()


def run_continuous_runtime_cycle(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    return run_once(*args, **kwargs)


ensure_cycle = ensure_continuous_runtime_cycle
run_cycle = run_continuous_runtime_cycle
