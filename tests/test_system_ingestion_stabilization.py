from runtime_core.system_ingestion.analyzer import Analyzer
from runtime_core.system_ingestion.component_extractor import extract_component_graph
from runtime_core.system_ingestion.comparator import Comparator
from runtime_core.system_ingestion.intake_graph import build_system_intake_graph


def test_system_ingestion_analyzer_decomposes_reviewable_system_payload():
    analysis = Analyzer().analyze(
        {
            "name": "legacy research workflow",
            "description": "Manual upload and spreadsheet handoff with fragmented dashboard, no validation, missing lineage, and disconnected queue routing.",
        }
    )

    assert analysis["status"] == "success"
    assert analysis["component_count"] >= 3
    assert analysis["gap_count"] >= 2
    assert analysis["redesign_required"] is True
    assert analysis["confidence"] > 0.5


def test_system_ingestion_comparator_returns_redesign_recommendations():
    analysis = Analyzer().analyze(
        "source ingestion, queue routing, dashboard portal, memory index, weak validation, missing lineage"
    )
    comparison = Comparator().compare(analysis)

    assert comparison["status"] == "success"
    assert comparison["comparison_type"] == "system_redesign_readiness"
    assert comparison["redesign_priority"] == "high"
    assert comparison["redesign_recommendations"]
    assert "resolve_missing_lineage" in comparison["redesign_recommendations"]


def test_system_intake_graph_normalizes_governed_source_nodes():
    graph = build_system_intake_graph(
        {
            "system_name": "claims workflow",
            "sources": [
                {"source_type": "repo", "path": "src/claims", "summary": "service modules and api routes"},
                {"type": "docs", "path": "docs/architecture.md", "summary": "workflow and user constraints"},
                {"label": "operator notes", "description": "manual spreadsheet handoff and weak validation"},
                {"type": "api", "uri": "openapi.json", "summary": "external integration contracts"},
            ],
        }
    )

    assert graph["status"] == "intake_graph_ready"
    assert graph["authority"]["runtime_truth_mutated"] is False
    assert graph["authority"]["secrets_logged"] is False
    assert graph["source_type_count"] >= 4
    assert {"repo", "docs", "api", "manual_description"} <= set(graph["source_types"])
    assert "interfaces" in graph["extraction_targets"]
    assert all(node["governance"]["requires_operator_review"] is True for node in graph["nodes"])


def test_analyzer_attaches_intake_graph_without_body_reads():
    analysis = Analyzer().analyze(
        {
            "system_name": "legacy compliance workflow",
            "sources": [
                {"source_type": "architecture_notes", "description": "workflow architecture integration gap"},
                {"source_type": "config", "description": "database queue routing no validation"},
            ],
        }
    )

    assert analysis["intake_graph"]["status"] == "intake_graph_ready"
    assert analysis["intake_graph"]["authority"]["body_reads_performed"] is False
    assert analysis["source_type_count"] == 2


def test_component_extractor_maps_review_safe_component_graph():
    intake = build_system_intake_graph(
        {
            "system_name": "claims workflow",
            "sources": [
                {"source_type": "repo", "path": "src/claims", "summary": "backend service modules with api endpoints"},
                {"source_type": "docs", "path": "docs/process.md", "summary": "operator approval workflow and user constraints"},
                {"source_type": "config", "path": "settings.yaml", "summary": "database queue routing and security validation"},
                {"source_type": "manual_description", "description": "manual spreadsheet handoff creates bottleneck and missing lineage"},
            ],
        }
    )
    graph = extract_component_graph(intake)

    assert graph["status"] == "component_graph_ready"
    assert graph["component_count"] >= 7
    assert {"service", "module", "workflow", "data_store", "interface", "user_actor", "constraint"} <= set(graph["component_types"])
    assert {"manual", "bottleneck", "missing_lineage"} <= set(graph["risk_points"])
    assert graph["replacement_candidates"]
    assert graph["authority"]["runtime_truth_mutated"] is False
    assert graph["authority"]["secrets_logged"] is False


def test_analyzer_attaches_component_graph_for_superior_system_inputs():
    analysis = Analyzer().analyze(
        {
            "system_name": "legacy claims workflow",
            "sources": [
                {"source_type": "api", "summary": "api endpoint integration contracts"},
                {"source_type": "screenshot", "summary": "operator screen and approval workflow"},
                {"source_type": "manual_description", "description": "manual handoff weak validation integration gap"},
            ],
        }
    )

    assert analysis["component_graph"]["status"] == "component_graph_ready"
    assert analysis["extracted_component_count"] >= 3
    assert "interface" in analysis["extracted_component_types"]
    assert analysis["component_graph"]["authority"]["body_reads_performed"] is False
