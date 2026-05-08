from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_RELATIVE_PATHS = [
    "src/frontend/command_center/modern/dashboard_architecture_map.json",
    "src/frontend/command_center/modern/lifecycle_stage_registry.json",
    "src/frontend/command_center/modern/runtime_surface_registry.json",
    "src/frontend/command_center/modern/route_surface_registry.json",
    "src/frontend/command_center/modern/runtime_truth_contract.json",
    "src/frontend/command_center/modern/runtime_truth_status.json",
    "src/frontend/command_center/modern/validation_authority_status.json",
    "src/frontend/command_center/modern/evidence_traceability_status.json",
    "src/frontend/command_center/modern/verified_memory_status.json",
    "src/frontend/command_center/modern/recursive_feedback_status.json",
    "exports/latest/dashboard_runtime_truth.json",
    "exports/latest/validation_authority_report.json",
    "exports/latest/evidence_traceability_index.json",
    "exports/latest/verified_memory_gate_report.json",
    "exports/latest/recursive_feedback_gate_report.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def flatten_json(value: Any, prefix: str = "") -> List[str]:
    rows: List[str] = []

    def walk(node: Any, path: str) -> None:
        if node is None:
            return
        if isinstance(node, dict):
            for key, item in node.items():
                next_path = f"{path}.{key}" if path else str(key)
                walk(item, next_path)
            return
        if isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f"{path}[{index}]")
            return
        rows.append(f"{path}: {node}")

    walk(value, prefix)
    return rows


def read_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        return value if isinstance(value, dict) else {"value": value}
    except Exception:
        return None


def build_dashboard_intelligence_index(project_root: Path, relative_paths: Iterable[str] = DEFAULT_RELATIVE_PATHS) -> Dict[str, Any]:
    documents: List[Dict[str, Any]] = []

    for relative in relative_paths:
        path = project_root / relative
        data = read_json(path)
        if data is None:
            documents.append({
                "path": relative,
                "status": "missing",
                "title": Path(relative).name,
                "text": "",
                "terms": [],
            })
            continue

        rows = flatten_json(data)
        text = "\n".join(rows)
        terms = sorted({
            token.strip(".,:;()[]{}<>\"'").lower()
            for token in text.replace("\n", " ").split(" ")
            if len(token.strip(".,:;()[]{}<>\"'")) >= 3
        })

        documents.append({
            "path": relative,
            "status": "indexed",
            "title": Path(relative).name,
            "text": text[:50000],
            "term_count": len(terms),
            "terms": terms[:2000],
        })

    indexed = [doc for doc in documents if doc["status"] == "indexed"]

    return {
        "schema": "claire.dashboard_intelligence_index.v1",
        "version": "17.62",
        "generated_at": utc_now(),
        "mode": "local_dashboard_truth_search",
        "standalone_intelligence_ready": False,
        "standalone_note": "This is the local index foundation for a future standalone Claire intelligence engine.",
        "documents_total": len(documents),
        "documents_indexed": len(indexed),
        "documents_missing": len(documents) - len(indexed),
        "documents": documents,
    }
