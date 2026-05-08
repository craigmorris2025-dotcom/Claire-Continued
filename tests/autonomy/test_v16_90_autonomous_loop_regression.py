
from pathlib import Path

from claire.autonomy.runtime_cycle_manager import start_runtime_cycle, advance_runtime_cycle, stop_runtime_cycle
from claire.autonomy.autonomous_escalation_engine import evaluate_autonomous_escalations
from claire.autonomy.recursive_orchestration_controller import run_recursive_orchestration_controller
from claire.autonomy.adaptive_runtime_reprioritization import build_adaptive_runtime_reprioritization
from claire.memory.strategic_memory_registry import add_strategic_memory
from claire.orchestration.intelligence_task_registry import register_intelligence_task


def test_runtime_cycle_manager_bounds_cycles():
    cycle = start_runtime_cycle(max_cycles=1)
    updated = advance_runtime_cycle(cycle["cycle_id"], {"type": "regression"})
    assert updated["status"] == "completed"
    assert updated["stop_reason"] == "max_cycles_reached"
    assert Path("data/autonomy/runtime_cycle_state.json").exists()


def test_runtime_cycle_manager_stop():
    cycle = start_runtime_cycle(max_cycles=3)
    stopped = stop_runtime_cycle(cycle["cycle_id"], "operator_stop")
    assert stopped["status"] == "stopped"


def test_autonomous_escalation_engine_builds_state():
    add_strategic_memory(
        memory_type="thesis",
        title="High priority regression thesis",
        payload={"summary": "test"},
        confidence=0.9,
    )
    state = evaluate_autonomous_escalations(threshold=0.7)
    assert state["status"] == "ready"
    assert Path("data/autonomy/autonomous_escalation_state.json").exists()


def test_recursive_orchestration_controller_is_bounded():
    register_intelligence_task(
        task_type="signal_analysis",
        title="High priority recursive regression task",
        priority=10,
    )
    state = run_recursive_orchestration_controller(threshold=0.7, max_follow_on_tasks=2)
    assert state["status"] == "completed"
    assert state["created_task_count"] <= 2
    assert Path("data/autonomy/recursive_orchestration_state.json").exists()


def test_adaptive_runtime_reprioritization_builds():
    state = build_adaptive_runtime_reprioritization()
    assert state["status"] == "ready"
    assert "adjusted_priorities" in state
    assert Path("data/autonomy/adaptive_runtime_reprioritization.json").exists()
