from __future__ import annotations

import importlib
from pathlib import Path


def test_s471_registry_contains_uploaded_document_knowledge_base():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    registry = module.build_s471_knowledge_document_registry()
    assert registry["ready"] is True
    assert registry["document_count"] >= 15

    doc_ids = set(registry["doc_ids"])
    assert "claire_master_system_build_plan" in doc_ids
    assert "claire_governance_and_safety" in doc_ids
    assert "claire_enterprise_update_governance" in doc_ids
    assert "claire_technology_database" in doc_ids


def test_s472_domain_ontology_maps_core_domains():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    ontology = module.build_s472_domain_ontology_contract()
    domain_map = ontology["ontology"]["domain_to_documents"]

    for domain in ["governance", "lifecycle", "portfolio", "breakthrough", "acquisition", "engineering", "recursive_learning"]:
        assert domain in domain_map
        assert domain_map[domain]


def test_s473_search_registry_finds_relevant_docs():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    governance = module.search_knowledge_registry("governance safety redline compliance", domains=["governance"])
    assert governance["results"]
    assert governance["results"][0]["doc_id"] in {
        "claire_governance_and_safety",
        "claire_unified_platform_definition_v1",
        "claire_master_system_build_plan",
    }

    update = module.search_knowledge_registry("online update rollback approval staged validation", domains=["update_governance"])
    assert any(result["doc_id"] == "claire_enterprise_update_governance" for result in update["results"])

    tech = module.search_knowledge_registry("technology maturity compatibility engineering complexity", domains=["technology_intelligence"])
    assert any(result["doc_id"] == "claire_technology_database" for result in tech["results"])


def test_s474_route_anchor_map_contains_core_routes():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    route = module.build_s474_route_anchor_contract()
    route_map = route["route_anchor_map"]

    assert "portfolio_path" in route_map
    assert "breakthrough_design_path" in route_map
    assert "recursive_self_ingestion" in route_map
    assert "online_update_readiness" in route_map


def test_s475_source_trust_prioritizes_governing_sources():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    trust = module.build_s475_source_trust_and_freshness_contract()
    assert trust["trust_tiers"]["governing"]["weight"] > trust["trust_tiers"]["architectural"]["weight"]
    assert trust["trust_counts"]["governing"] >= 3
    assert "Governance and safety documents override convenience or speed." in trust["rules"]


def test_s476_assets_exist_and_preserve_authority_flags():
    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_knowledge_base_registry.js"
    css = root / "frontend/cockpit/shell/assets/claire_knowledge_base_registry.css"

    assert js.exists()
    assert css.exists()

    text = js.read_text(encoding="utf-8")
    assert "ClaireKnowledgeBaseRegistryVersion" in text
    assert "runtimeTruthMutationAllowed: false" in text
    assert "liveWebExecutionEnabled: false" in text
    assert "networkRequestPerformed: false" in text


def test_registry_exports_evidence_sources_compatible_with_s464():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")
    evidence_model = importlib.import_module("claire.api.claire_evidence_backed_answer_model_s464_s470")

    sources = module.registry_documents_as_evidence_sources(domains=["governance"])
    assert sources
    assert all("source_id" in source for source in sources)

    answer = evidence_model.build_evidence_backed_answer(
        "What is Claire's governance boundary?",
        sources=sources,
    )
    assert answer["evidence_basket"]["source_count"] == len(sources)
    assert answer["answer_quality_state"] in {"evidence_backed", "verification_needed"}


def test_s477_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    gate = module.build_s477_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["update_search_finds_update_governance"] is True
    assert (tmp_path / "s477_claire_knowledge_base_registry_stop_gate.json").exists()


def test_s471_s477_rollup_ready():
    module = importlib.import_module("claire.api.claire_knowledge_base_registry_s471_s477")

    rollup = module.build_claire_knowledge_base_registry_s471_s477(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s471"]["document_count"] >= 15
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
