from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/discovery/governed_research_synthesis_engine.py", r"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.discovery.discovery_campaign_manager import list_discovery_campaigns
from claire.discovery.thesis_graph_engine import load_thesis_graph
from claire.discovery.opportunity_landscape_generator import build_opportunity_landscape
from claire.orchestration.evidence_fusion_coordinator import build_evidence_fusion_state
from claire.memory.longitudinal_confidence_engine import calculate_longitudinal_confidence


RESEARCH_SYNTHESIS_PATH = Path("data/discovery/governed_research_synthesis.json")


def build_governed_research_synthesis() -> Dict[str, Any]:
    campaigns = list_discovery_campaigns()
    graph = load_thesis_graph()
    landscape = build_opportunity_landscape()
    fusion = build_evidence_fusion_state()
    confidence = calculate_longitudinal_confidence()

    synthesis = {
        "version": "16.94",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "campaign_count": len(campaigns),
        "active_campaign_count": len([c for c in campaigns if c.get("state") == "active"]),
        "thesis_graph_summary": {
            "node_count": len(graph.get("nodes", [])),
            "edge_count": len(graph.get("edges", [])),
        },
        "opportunity_landscape_summary": landscape.get("summary", {}),
        "evidence_fusion_summary": {
            "total_records": fusion.get("total_records", 0),
            "source_counts": fusion.get("source_counts", {}),
        },
        "longitudinal_confidence": confidence.get("longitudinal_confidence", 0.0),
        "synthesis_notes": [
            "Research synthesis is governed and evidence-aware.",
            "Quarantined sources remain visible but excluded from high-confidence scoring.",
            "Operator review remains required before buyer-facing or pilot-facing claims.",
        ],
        "next_actions": [
            "Add supporting and conflicting evidence nodes to thesis graph.",
            "Create at least one active discovery campaign per pilot domain.",
            "Link opportunity candidates to proof records and lineage records.",
        ],
    }

    RESEARCH_SYNTHESIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESEARCH_SYNTHESIS_PATH.write_text(json.dumps(synthesis, indent=2), encoding="utf-8")
    return synthesis
""")

print("v16.94 governed research synthesis engine installed.")
