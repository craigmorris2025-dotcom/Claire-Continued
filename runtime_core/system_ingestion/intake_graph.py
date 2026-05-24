"""Governed source intake graph for external system analysis."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


SOURCE_TYPES: dict[str, dict[str, Any]] = {
    "repo": {
        "aliases": {"repo", "repository", "codebase", "source code", "git"},
        "extracts": ["services", "modules", "interfaces", "configs"],
    },
    "docs": {
        "aliases": {"doc", "docs", "documentation", "readme", "spec"},
        "extracts": ["workflows", "users", "constraints", "requirements"],
    },
    "architecture_notes": {
        "aliases": {"architecture", "diagram", "notes", "system map", "blueprint"},
        "extracts": ["components", "dependencies", "data_flow", "control_flow"],
    },
    "config": {
        "aliases": {"config", "configuration", "env", "yaml", "toml", "json"},
        "extracts": ["settings", "secrets_boundary", "runtime_dependencies"],
    },
    "api": {
        "aliases": {"api", "endpoint", "openapi", "swagger", "route"},
        "extracts": ["interfaces", "contracts", "integration_points"],
    },
    "screenshot": {
        "aliases": {"screenshot", "screen", "ui capture", "image"},
        "extracts": ["screens", "user_actions", "workflow_surfaces"],
    },
    "manual_description": {
        "aliases": {"manual", "description", "operator notes", "workflow description", "text"},
        "extracts": ["workflows", "constraints", "known_gaps"],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(_as_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_as_text(item) for item in value.values())
    return str(value)


def _classify_source(raw: dict[str, Any]) -> str:
    explicit = str(raw.get("source_type") or raw.get("type") or "").strip().lower().replace(" ", "_")
    if explicit in SOURCE_TYPES:
        return explicit
    searchable = " ".join(
        str(raw.get(key) or "").lower()
        for key in ("source_type", "type", "name", "label", "path", "uri", "description")
    )
    if "operator" in searchable or "manual" in searchable:
        return "manual_description"
    for source_type, config in SOURCE_TYPES.items():
        if any(alias in searchable for alias in config["aliases"]):
            return source_type
    return "manual_description"


def _normalize_source(raw: dict[str, Any], index: int) -> dict[str, Any]:
    source_type = _classify_source(raw)
    label = str(raw.get("label") or raw.get("name") or raw.get("path") or raw.get("uri") or f"source {index + 1}")
    locator = str(raw.get("path") or raw.get("uri") or raw.get("locator") or "")
    summary = _as_text(raw.get("summary") or raw.get("description") or raw.get("content"))
    evidence_kind = "file_reference" if locator else "operator_supplied_description"
    return {
        "node_id": _stable_id("source", source_type, label, locator, index),
        "node_type": "intake_source",
        "source_type": source_type,
        "label": label,
        "locator": locator,
        "summary": summary[:700],
        "evidence_kind": evidence_kind,
        "extracts": SOURCE_TYPES[source_type]["extracts"],
        "governance": {
            "body_read_allowed": False,
            "secret_capture_allowed": False,
            "runtime_truth_mutation_allowed": False,
            "requires_operator_review": True,
        },
    }


def build_system_intake_graph(payload: dict[str, Any] | str | None) -> dict[str, Any]:
    """Build the first graph layer: governed intake source nodes and extraction plan."""
    if payload is None:
        raw_sources: list[dict[str, Any]] = []
        system_label = "Unspecified system"
    elif isinstance(payload, str):
        raw_sources = [{"source_type": "manual_description", "label": "manual system description", "description": payload}]
        system_label = "Operator-described system"
    else:
        system_label = str(payload.get("system_name") or payload.get("name") or "External system")
        candidates = payload.get("sources") or payload.get("intake_sources") or []
        raw_sources = candidates if isinstance(candidates, list) else []
        if not raw_sources:
            raw_sources = [{"source_type": "manual_description", "label": system_label, "description": _as_text(payload)}]

    sources = [_normalize_source(source if isinstance(source, dict) else {"description": source}, idx) for idx, source in enumerate(raw_sources)]
    source_types = sorted({source["source_type"] for source in sources})
    extraction_targets = sorted({target for source in sources for target in source["extracts"]})
    edges = [
        {
            "edge_id": _stable_id("edge", "system", source["node_id"]),
            "from": "system_under_review",
            "to": source["node_id"],
            "relationship": "has_intake_source",
            "status": "planned",
        }
        for source in sources
    ]
    return {
        "schema_version": "claire.system_intake_graph.v1",
        "status": "intake_graph_ready" if sources else "insufficient_intake_sources",
        "generated_at": _utc_now(),
        "system": {
            "node_id": "system_under_review",
            "label": system_label,
            "node_type": "external_system",
        },
        "nodes": sources,
        "edges": edges,
        "source_type_count": len(source_types),
        "source_types": source_types,
        "extraction_targets": extraction_targets,
        "next_layer": {
            "name": "component_extraction",
            "status": "not_started",
            "requires": ["operator_review", "source_allowlist", "secret_redaction_policy"],
        },
        "authority": {
            "read_only": True,
            "body_reads_performed": False,
            "secrets_logged": False,
            "runtime_truth_mutated": False,
            "operator_review_required": True,
        },
    }
