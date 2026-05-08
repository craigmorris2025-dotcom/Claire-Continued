from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/memory/cross_run_evidence_linker.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


EVIDENCE_LINK_PATH = Path("data/memory/cross_run_evidence_links.json")


def _load_links() -> List[Dict[str, Any]]:
    if not EVIDENCE_LINK_PATH.exists():
        return []
    try:
        data = json.loads(EVIDENCE_LINK_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def create_evidence_link(
    source_id: str,
    target_id: str,
    relationship: str,
    rationale: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = {
        "version": "16.67",
        "link_id": f"link_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_id": source_id,
        "target_id": target_id,
        "relationship": relationship,
        "rationale": rationale,
        "metadata": metadata or {},
        "status": "active",
    }

    EVIDENCE_LINK_PATH.parent.mkdir(parents=True, exist_ok=True)
    links = _load_links()
    links.append(record)
    EVIDENCE_LINK_PATH.write_text(json.dumps(links, indent=2), encoding="utf-8")
    return record


def list_evidence_links(entity_id: str | None = None) -> List[Dict[str, Any]]:
    links = _load_links()
    if entity_id is None:
        return links
    return [
        link for link in links
        if link.get("source_id") == entity_id or link.get("target_id") == entity_id
    ]
""")

print("v16.67 cross-run evidence linker installed.")
