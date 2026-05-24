from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TechnologyNode:
    id: str
    name: str
    family: str
    year_start: int | None = None
    year_end: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TechnologyEdge:
    from_id: str
    to_id: str
    reason: str | None = None
    enabling_signals: list[str] = field(default_factory=list)
    pattern_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TechnologyGraph:
    def __init__(self, nodes: list[TechnologyNode], edges: list[TechnologyEdge]):
        self.nodes = nodes
        self.edges = edges
        self._nodes_by_id = {node.id: node for node in nodes}
        self._edges_from: dict[str, list[TechnologyEdge]] = {}
        self._edges_to: dict[str, list[TechnologyEdge]] = {}
        for edge in edges:
            self._edges_from.setdefault(edge.from_id, []).append(edge)
            self._edges_to.setdefault(edge.to_id, []).append(edge)

    def get_node(self, node_id: str) -> TechnologyNode | None:
        return self._nodes_by_id.get(node_id)

    def edges_from(self, node_id: str) -> list[TechnologyEdge]:
        return self._edges_from.get(node_id, [])

    def edges_to(self, node_id: str) -> list[TechnologyEdge]:
        return self._edges_to.get(node_id, [])


def graph_from_lineage(lineage: dict[str, Any]) -> TechnologyGraph:
    nodes = [
        TechnologyNode(
            id=str(item.get("id")),
            name=str(item.get("name") or item.get("id")),
            family=", ".join(item.get("domains", [])) if isinstance(item.get("domains"), list) else "unknown",
            year_start=item.get("year") if isinstance(item.get("year"), int) else None,
            metadata=item,
        )
        for item in lineage.get("nodes", [])
        if isinstance(item, dict) and item.get("id")
    ]
    edges = [
        TechnologyEdge(
            from_id=str(item.get("from_id")),
            to_id=str(item.get("to_id")),
            reason=item.get("logic_shift") or item.get("relationship"),
            enabling_signals=item.get("capability_delta", []) if isinstance(item.get("capability_delta"), list) else [],
            pattern_ids=item.get("transformation_pattern", []) if isinstance(item.get("transformation_pattern"), list) else [],
            metadata=item,
        )
        for item in lineage.get("edges", [])
        if isinstance(item, dict) and item.get("from_id") and item.get("to_id")
    ]
    return TechnologyGraph(nodes, edges)


__all__ = ["TechnologyEdge", "TechnologyGraph", "TechnologyNode", "graph_from_lineage"]
