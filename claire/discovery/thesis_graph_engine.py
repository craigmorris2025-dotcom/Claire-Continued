
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


THESIS_GRAPH_PATH = Path("data/discovery/thesis_graph.json")

VALID_NODE_TYPES = {
    "signal",
    "thesis",
    "evidence",
    "counter_evidence",
    "opportunity",
    "risk",
    "portfolio_implication",
}

VALID_EDGE_TYPES = {
    "supports",
    "contradicts",
    "extends",
    "depends_on",
    "implies",
    "weakens",
}


def _load_graph() -> Dict[str, Any]:
    if not THESIS_GRAPH_PATH.exists():
        return {"version": "16.92", "nodes": [], "edges": []}
    try:
        data = json.loads(THESIS_GRAPH_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("nodes", [])
            data.setdefault("edges", [])
            return data
    except Exception:
        pass
    return {"version": "16.92", "nodes": [], "edges": []}


def add_thesis_node(node_type: str, title: str, payload: Dict[str, Any] | None = None, confidence: float = 0.5) -> Dict[str, Any]:
    if node_type not in VALID_NODE_TYPES:
        raise ValueError(f"Invalid thesis node type: {node_type}")

    node = {
        "node_id": f"node_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "node_type": node_type,
        "title": title,
        "payload": payload or {},
        "confidence": max(0.0, min(1.0, float(confidence))),
        "status": "active",
    }

    graph = _load_graph()
    graph["nodes"].append(node)
    THESIS_GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    THESIS_GRAPH_PATH.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return node


def add_thesis_edge(source_node_id: str, target_node_id: str, edge_type: str, rationale: str) -> Dict[str, Any]:
    if edge_type not in VALID_EDGE_TYPES:
        raise ValueError(f"Invalid thesis edge type: {edge_type}")

    graph = _load_graph()
    node_ids = {node.get("node_id") for node in graph.get("nodes", [])}
    if source_node_id not in node_ids or target_node_id not in node_ids:
        raise ValueError("Both source and target nodes must exist before creating an edge.")

    edge = {
        "edge_id": f"edge_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "edge_type": edge_type,
        "rationale": rationale,
        "status": "active",
    }

    graph["edges"].append(edge)
    THESIS_GRAPH_PATH.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return edge


def load_thesis_graph() -> Dict[str, Any]:
    return _load_graph()
