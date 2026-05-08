from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/discovery/opportunity_landscape_generator.py", r"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from claire.discovery.thesis_graph_engine import load_thesis_graph


OPPORTUNITY_LANDSCAPE_PATH = Path("data/discovery/opportunity_landscape.json")


def build_opportunity_landscape() -> Dict[str, Any]:
    graph = load_thesis_graph()
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    opportunities = [node for node in nodes if node.get("node_type") == "opportunity"]
    theses = [node for node in nodes if node.get("node_type") == "thesis"]
    risks = [node for node in nodes if node.get("node_type") == "risk"]
    evidence = [node for node in nodes if node.get("node_type") in {"evidence", "counter_evidence"}]

    type_counts = Counter(node.get("node_type", "unknown") for node in nodes)

    landscape = {
        "version": "16.93",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "summary": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "opportunity_count": len(opportunities),
            "thesis_count": len(theses),
            "risk_count": len(risks),
            "evidence_count": len(evidence),
            "node_type_counts": dict(type_counts),
        },
        "clusters": [
            {
                "cluster_name": "opportunity_candidates",
                "items": opportunities,
                "note": "Candidate opportunities require evidence depth and operator review before pilot or acquisition packaging.",
            },
            {
                "cluster_name": "active_theses",
                "items": theses,
                "note": "Theses should be linked to supporting and conflicting evidence.",
            },
            {
                "cluster_name": "risk_and_counter_evidence",
                "items": risks + [node for node in nodes if node.get("node_type") == "counter_evidence"],
                "note": "Risks and counter-evidence preserve falsifiability.",
            },
        ],
    }

    OPPORTUNITY_LANDSCAPE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPPORTUNITY_LANDSCAPE_PATH.write_text(json.dumps(landscape, indent=2), encoding="utf-8")
    return landscape
""")

print("v16.93 opportunity landscape generator installed.")
