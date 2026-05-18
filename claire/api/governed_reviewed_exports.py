from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(encoded).hexdigest()[:16]}"

def export_reviewed_output(review_item: Mapping[str, Any], *, export_dir: Path | None = None, export_format: str = "json") -> Dict[str, Any]:
    if review_item.get("status") not in {"approved", "export_only"}:
        raise PermissionError("Only approved or export_only review items may be exported.")
    out_dir = export_dir or Path.cwd() / "exports" / "governed_outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "export_version": "S88",
        "created_at": _utc_now(),
        "review_item_id": review_item.get("review_item_id"),
        "decision_status": review_item.get("status"),
        "route": review_item.get("route"),
        "headline": review_item.get("headline"),
        "source_evidence_ids": list(review_item.get("source_evidence_ids") or []),
        "payload": review_item.get("payload"),
        "audit": {
            "decided_at": review_item.get("decided_at"),
            "decided_by": review_item.get("decided_by"),
            "decision_note": review_item.get("decision_note"),
            "runtime_truth_write": "blocked",
            "export_is_derived_artifact": True,
        },
    }
    export_id = _stable_id("export", payload)
    path = out_dir / f"{export_id}.{export_format}"
    if export_format == "json":
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    elif export_format == "md":
        body = [
            f"# {payload['headline']}",
            "",
            f"- Export ID: `{export_id}`",
            f"- Route: `{payload['route']}`",
            f"- Review status: `{payload['decision_status']}`",
            f"- Runtime truth write: `blocked`",
            "",
            "## Summary",
            "",
            str((payload.get("payload") or {}).get("summary", "")),
        ]
        path.write_text("\n".join(body), encoding="utf-8")
    else:
        raise ValueError("export_format must be json or md")
    return {
        "export_id": export_id,
        "export_version": "S88",
        "status": "exported",
        "path": str(path),
        "format": export_format,
        "review_item_id": review_item.get("review_item_id"),
        "runtime_truth_write": "blocked",
        "derived_artifact": True,
    }
