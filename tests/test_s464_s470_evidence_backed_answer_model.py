from __future__ import annotations

import importlib
from pathlib import Path


def test_s464_evidence_source_schema_and_default_sources():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    schema = module.build_s464_evidence_source_schema()
    assert schema["ready"] is True
    assert "source_id" in schema["source_fields"]
    assert "governance_contract" in schema["source_types"]

    sources = module.build_default_claire_evidence_sources()
    assert len(sources) >= 5
    ids = {source["source_id"] for source in sources}
    assert "claire_master_build_plan" in ids
    assert "claire_governance_safety" in ids


def test_s465_evidence_quality_scoring_grades_sources():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    strong = module.make_evidence_source(
        "strong_source",
        "Strong Source",
        "governance_contract",
        "Strong governance source.",
        relevance=0.95,
        specificity=0.95,
        recency=0.85,
        supports=["claim_a", "claim_b"],
    )
    strong_score = module.score_evidence_source(strong)
    assert strong_score["grade"] == "strong"

    weak = module.make_evidence_source(
        "weak_source",
        "Weak Source",
        "general_context",
        "Weak source.",
        relevance=0.10,
        specificity=0.10,
        trust=0.10,
        recency=0.10,
        limitations=["unverified", "generic", "no corroboration"],
    )
    weak_score = module.score_evidence_source(weak)
    assert weak_score["grade"] in {"weak", "insufficient"}


def test_s466_evidence_basket_support_summary():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    basket = module.build_evidence_basket("Can Claire evaluate this engineering trend for innovation potential?")
    assert basket["source_count"] >= 5
    assert basket["support_summary"]["support_level"] in {"strong", "usable", "limited", "insufficient"}
    assert basket["classification"]["domain"] in {"engineering", "market", "breakthrough", "research", "general"}
    assert basket["network_request_performed"] is False


def test_s467_claim_support_marks_strong_and_weak_cases():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    strong_basket = module.build_evidence_basket("What is Claire's governance boundary?")
    strong_claim = module.classify_claim_support("Claire has blocked runtime mutation.", strong_basket, "contractual")
    assert strong_claim["status"] in {"supported", "partially_supported"}
    assert strong_claim["evidence_ids"]

    weak_source = module.make_evidence_source(
        "weak_note",
        "Weak Note",
        "general_context",
        "Unsupported note.",
        relevance=0.1,
        specificity=0.1,
        trust=0.1,
        recency=0.1,
        limitations=["not verified", "no support"],
    )
    weak_basket = module.build_evidence_basket("Can Claire prove this unsupported claim?", sources=[weak_source])
    weak_claim = module.classify_claim_support("Unsupported claim.", weak_basket, "high")
    assert weak_claim["status"] in {"needs_verification", "inference", "unsupported"}
    assert weak_claim["verification_needed"]


def test_s468_evidence_backed_answer_uses_s450_and_s457_contracts_and_remains_safe():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    answer = module.build_evidence_backed_answer(
        "Can Claire analyze this market trend and identify an innovation route?",
        context={"payload": "available"},
    )

    assert answer["classification"]["domain"] == "market"
    assert answer["response_card"]["card_type"] == "answer"
    assert answer["evidence_basket"]["source_count"] >= 5
    assert answer["claims"]
    assert answer["answer_quality_state"] in {"evidence_backed", "verification_needed"}

    for flag in module.BLOCKED_AUTHORITY:
        assert answer[flag] is False


def test_s469_traceability_contract_and_assets():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    trace = module.build_s469_traceability_contract()
    assert "evidence_ids" in trace["trace_fields"]
    assert "verification_needed" in trace["trace_fields"]

    root = Path.cwd()
    js = root / "frontend/cockpit/shell/assets/claire_evidence_backed_answers.js"
    css = root / "frontend/cockpit/shell/assets/claire_evidence_backed_answers.css"

    assert js.exists()
    assert css.exists()

    js_text = js.read_text(encoding="utf-8")
    assert "ClaireEvidenceBackedAnswersVersion" in js_text
    assert "runtimeTruthMutationAllowed: false" in js_text
    assert "liveWebExecutionEnabled: false" in js_text
    assert "networkRequestPerformed: false" in js_text


def test_s470_stop_gate_allows_forward_motion(tmp_path):
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    gate = module.build_s470_stop_gate(report_dir=tmp_path, project_root=Path.cwd())
    assert gate["ok"] is True
    assert gate["ready"] is True
    assert gate["forward_motion_allowed"] is True
    assert gate["checks"]["weak_answer_marks_verification_needed"] is True
    assert (tmp_path / "s470_claire_evidence_backed_answer_model_stop_gate.json").exists()


def test_s464_s470_rollup_ready():
    module = importlib.import_module("runtime_core.api.evidence_backed_answer_model_s464_s470")

    rollup = module.build_evidence_backed_answer_model_s464_s470(project_root=Path.cwd())
    assert rollup["ready"] is True
    assert rollup["contracts"]["s464"]["ready"] is True
    assert rollup["stop_gate"]["forward_motion_allowed"] is True
    assert rollup["runtime_truth_mutation_allowed"] is False
    assert rollup["automatic_updates_enabled"] is False
