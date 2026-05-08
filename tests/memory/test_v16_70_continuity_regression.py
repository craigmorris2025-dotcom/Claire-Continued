
from pathlib import Path

from claire.memory.strategic_memory_registry import add_strategic_memory, list_strategic_memories
from claire.memory.cross_run_evidence_linker import create_evidence_link, list_evidence_links
from claire.memory.longitudinal_confidence_engine import calculate_longitudinal_confidence
from claire.memory.operator_reinforcement_feedback import record_operator_feedback, list_operator_feedback


def test_strategic_memory_registry_adds_memory():
    memory = add_strategic_memory(
        memory_type="thesis",
        title="Regression thesis memory",
        payload={"summary": "test continuity thesis"},
        confidence=0.6,
        tags=["regression"],
    )
    assert memory["memory_type"] == "thesis"
    assert Path("data/memory/strategic_memory_registry.json").exists()


def test_cross_run_evidence_linker_creates_link():
    link = create_evidence_link(
        source_id="source_regression",
        target_id="target_regression",
        relationship="supports",
        rationale="Regression continuity proof.",
    )
    assert link["relationship"] == "supports"
    assert len(list_evidence_links()) >= 1


def test_operator_feedback_records_memory():
    feedback = record_operator_feedback(
        target_id="target_regression",
        feedback="approved",
        rationale="Regression approval.",
    )
    assert feedback["feedback"] == "approved"
    assert len(list_operator_feedback()) >= 1


def test_longitudinal_confidence_engine_outputs_state():
    state = calculate_longitudinal_confidence()
    assert state["status"] == "ready"
    assert 0.0 <= state["longitudinal_confidence"] <= 1.0
    assert Path("data/memory/longitudinal_confidence_state.json").exists()
