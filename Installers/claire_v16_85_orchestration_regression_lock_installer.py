from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("tests/orchestration/test_v16_85_orchestration_regression.py", r"""
from pathlib import Path

from claire.orchestration.intelligence_task_registry import register_intelligence_task, list_intelligence_tasks
from claire.orchestration.bounded_orchestration_scheduler import run_bounded_orchestration_scheduler
from claire.orchestration.evidence_fusion_coordinator import build_evidence_fusion_state
from claire.orchestration.strategic_priority_engine import build_strategic_priority_state
from claire.memory.strategic_memory_registry import add_strategic_memory

def test_intelligence_task_registry_registers_task():
    task = register_intelligence_task(
        task_type="signal_analysis",
        title="Regression signal analysis task",
        payload={"summary": "test"},
        priority=8,
    )
    assert task["state"] == "queued"
    assert len(list_intelligence_tasks()) >= 1
    assert Path("data/orchestration/intelligence_task_registry.json").exists()

def test_bounded_orchestration_scheduler_completes():
    register_intelligence_task(
        task_type="evidence_review",
        title="Regression evidence review task",
        priority=7,
    )
    state = run_bounded_orchestration_scheduler(max_concurrent=2, max_tasks=5)
    assert state["status"] == "completed"
    assert Path("data/orchestration/bounded_orchestration_scheduler.json").exists()

def test_evidence_fusion_state_builds():
    fusion = build_evidence_fusion_state()
    assert fusion["status"] == "ready"
    assert "source_counts" in fusion
    assert Path("data/orchestration/evidence_fusion_state.json").exists()

def test_strategic_priority_state_builds():
    add_strategic_memory(
        memory_type="thesis",
        title="Regression orchestration thesis",
        payload={"summary": "test priority"},
        confidence=0.7,
    )
    state = build_strategic_priority_state()
    assert state["status"] == "ready"
    assert "ranked_tasks" in state
    assert "ranked_memories" in state
    assert Path("data/orchestration/strategic_priority_state.json").exists()
""")

print("v16.85 orchestration regression lock installed.")
print("Run: pytest tests/orchestration/test_v16_85_orchestration_regression.py")
