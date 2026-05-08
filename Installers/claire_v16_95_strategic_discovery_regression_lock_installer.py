from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("tests/discovery/test_v16_95_strategic_discovery_regression.py", r"""
from pathlib import Path

from claire.discovery.discovery_campaign_manager import create_discovery_campaign, list_discovery_campaigns
from claire.discovery.thesis_graph_engine import add_thesis_node, add_thesis_edge, load_thesis_graph
from claire.discovery.opportunity_landscape_generator import build_opportunity_landscape
from claire.discovery.governed_research_synthesis_engine import build_governed_research_synthesis


def test_discovery_campaign_manager_creates_campaign():
    campaign = create_discovery_campaign(
        title="Regression discovery campaign",
        objective="Validate governed discovery continuity.",
        domain="enterprise AI strategy",
    )
    assert campaign["state"] == "active"
    assert len(list_discovery_campaigns()) >= 1
    assert Path("data/discovery/discovery_campaigns.json").exists()


def test_thesis_graph_engine_creates_nodes_and_edges():
    thesis = add_thesis_node("thesis", "Regression thesis", {"summary": "test"}, confidence=0.7)
    evidence = add_thesis_node("evidence", "Regression evidence", {"summary": "supports thesis"}, confidence=0.8)
    edge = add_thesis_edge(evidence["node_id"], thesis["node_id"], "supports", "Evidence supports thesis.")
    graph = load_thesis_graph()

    assert edge["edge_type"] == "supports"
    assert len(graph["nodes"]) >= 2
    assert len(graph["edges"]) >= 1
    assert Path("data/discovery/thesis_graph.json").exists()


def test_opportunity_landscape_generator_builds():
    add_thesis_node("opportunity", "Regression opportunity", {"summary": "test opportunity"}, confidence=0.6)
    landscape = build_opportunity_landscape()
    assert landscape["status"] == "ready"
    assert "summary" in landscape
    assert Path("data/discovery/opportunity_landscape.json").exists()


def test_governed_research_synthesis_builds():
    synthesis = build_governed_research_synthesis()
    assert synthesis["status"] == "ready"
    assert "campaign_count" in synthesis
    assert "thesis_graph_summary" in synthesis
    assert Path("data/discovery/governed_research_synthesis.json").exists()
""")

print("v16.95 strategic discovery regression lock installed.")
print("Run: pytest tests/discovery/test_v16_95_strategic_discovery_regression.py")
