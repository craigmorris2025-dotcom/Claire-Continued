"""Deterministic component extraction for governed system intake graphs."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


COMPONENT_RULES: dict[str, dict[str, Any]] = {
    "service": {
        "terms": ["service", "worker", "backend", "daemon", "job"],
        "sources": {"repo", "architecture_notes", "manual_description"},
        "risk_terms": ["bottleneck", "single point", "manual"],
    },
    "module": {
        "terms": ["module", "package", "library", "class", "function"],
        "sources": {"repo"},
        "risk_terms": ["duplicate", "redundant", "fragmented"],
    },
    "workflow": {
        "terms": ["workflow", "process", "handoff", "queue", "approval"],
        "sources": {"docs", "screenshot", "manual_description", "architecture_notes"},
        "risk_terms": ["manual", "handoff", "copy paste", "bottleneck"],
    },
    "data_store": {
        "terms": ["database", "db", "warehouse", "storage", "index", "memory", "spreadsheet"],
        "sources": {"repo", "config", "architecture_notes", "manual_description"},
        "risk_terms": ["missing lineage", "untraced", "spreadsheet", "unknown quality"],
    },
    "interface": {
        "terms": ["api", "endpoint", "portal", "dashboard", "ui", "screen", "webhook"],
        "sources": {"api", "screenshot", "repo", "architecture_notes"},
        "risk_terms": ["disconnected", "integration gap", "silo", "fragmented"],
    },
    "user_actor": {
        "terms": ["user", "operator", "admin", "owner", "customer", "analyst"],
        "sources": {"docs", "screenshot", "manual_description"},
        "risk_terms": ["no approval", "ungoverned", "uncontrolled"],
    },
    "constraint": {
        "terms": ["constraint", "policy", "compliance", "validation", "permission", "security"],
        "sources": {"docs", "config", "manual_description", "architecture_notes"},
        "risk_terms": ["weak validation", "no validation", "unsafe", "unverified"],
    },
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256("::".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _text(*parts: Any) -> str:
    return " ".join(str(part or "") for part in parts).lower()


def _rule_matches(rule: dict[str, Any], source: dict[str, Any], text: str) -> tuple[bool, list[str]]:
    source_type = str(source.get("source_type") or "")
    matched_terms = [term for term in rule["terms"] if term in text]
    source_supported = source_type in rule["sources"]
    return bool(matched_terms or source_supported), matched_terms


def _risk_hints(rule: dict[str, Any], text: str) -> list[str]:
    return [term.replace(" ", "_") for term in rule["risk_terms"] if term in text]


def extract_component_graph(intake_graph: dict[str, Any] | None) -> dict[str, Any]:
    """Extract a review-safe component graph from normalized intake source nodes."""
    intake_graph = intake_graph or {}
    source_nodes = intake_graph.get("nodes") if isinstance(intake_graph.get("nodes"), list) else []
    component_nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for source in source_nodes:
        if not isinstance(source, dict):
            continue
        source_text = _text(source.get("label"), source.get("locator"), source.get("summary"), " ".join(source.get("extracts", [])))
        for component_type, rule in COMPONENT_RULES.items():
            matched, matched_terms = _rule_matches(rule, source, source_text)
            if not matched:
                continue
            risk_hints = _risk_hints(rule, source_text)
            node_id = _stable_id("component", source.get("node_id"), component_type)
            component_nodes.append(
                {
                    "node_id": node_id,
                    "node_type": "system_component",
                    "component_type": component_type,
                    "label": f"{component_type.replace('_', ' ')} from {source.get('label')}",
                    "source_node_id": source.get("node_id"),
                    "source_type": source.get("source_type"),
                    "matched_terms": matched_terms,
                    "risk_hints": risk_hints,
                    "review_state": "needs_operator_review" if risk_hints else "extracted_for_review",
                    "improvement_role": "replace_or_redesign" if risk_hints else "preserve_or_validate",
                }
            )
            edges.append(
                {
                    "edge_id": _stable_id("edge", source.get("node_id"), node_id),
                    "from": source.get("node_id"),
                    "to": node_id,
                    "relationship": "yields_component",
                    "status": "extracted_for_review",
                }
            )

    component_types = sorted({node["component_type"] for node in component_nodes})
    risk_points = sorted({risk for node in component_nodes for risk in node["risk_hints"]})
    return {
        "schema_version": "claire.system_component_graph.v1",
        "status": "component_graph_ready" if component_nodes else "no_components_extracted",
        "generated_at": _utc_now(),
        "system_node_id": intake_graph.get("system", {}).get("node_id", "system_under_review")
        if isinstance(intake_graph.get("system"), dict)
        else "system_under_review",
        "nodes": component_nodes,
        "edges": edges,
        "component_count": len(component_nodes),
        "component_types": component_types,
        "risk_points": risk_points,
        "preserve_candidates": [node["node_id"] for node in component_nodes if node["improvement_role"] == "preserve_or_validate"],
        "replacement_candidates": [node["node_id"] for node in component_nodes if node["improvement_role"] == "replace_or_redesign"],
        "next_layer": {
            "name": "dependency_and_flow_mapping",
            "status": "not_started",
            "requires": ["operator_review", "component_confirmation"],
        },
        "authority": {
            "read_only": True,
            "body_reads_performed": False,
            "secrets_logged": False,
            "runtime_truth_mutated": False,
            "operator_review_required": True,
        },
    }
