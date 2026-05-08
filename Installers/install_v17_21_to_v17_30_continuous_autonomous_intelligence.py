# Claire Syntalion Installer
# v17.21-v17.30 Continuous Autonomous Intelligence Infrastructure
#
# Place this file in the Claire project root and run:
#
#     python install_v17_21_to_v17_30_continuous_autonomous_intelligence.py
#
# Then test:
#
#     python -m pytest tests/continuous_autonomous_intelligence -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CLAIRE = SRC / "claire"
LAYER = CLAIRE / "continuous_autonomous_intelligence"
TESTS = ROOT / "tests" / "continuous_autonomous_intelligence"
DATA = ROOT / "data" / "continuous_autonomous_intelligence"
DOCS = ROOT / "docs" / "continuous_autonomous_intelligence"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    print("Installing Claire v17.21-v17.30 Continuous Autonomous Intelligence Infrastructure...")

    write_file(LAYER / "__init__.py", """
from .runtime import ContinuousAutonomousIntelligenceRuntime
from .worker_registry import WorkerRegistry
from .event_bus import SignalEventBus
from .priority_router import IngestionPriorityRouter
from .runtime_supervisor import RuntimeSupervisor
from .heartbeat_monitor import HeartbeatMonitor
from .state_recovery import StateRecoveryManager
from .campaign_continuity import CampaignContinuityManager
from .conflict_reconciliation import SignalConflictReconciler
from .escalation_contracts import EventDrivenEscalationEngine
from .continuous_regression_lock import ContinuousIntelligenceRegressionLock

__all__ = [
    "ContinuousAutonomousIntelligenceRuntime",
    "WorkerRegistry",
    "SignalEventBus",
    "IngestionPriorityRouter",
    "RuntimeSupervisor",
    "HeartbeatMonitor",
    "StateRecoveryManager",
    "CampaignContinuityManager",
    "SignalConflictReconciler",
    "EventDrivenEscalationEngine",
    "ContinuousIntelligenceRegressionLock",
]
""")

    write_file(LAYER / "models.py", """
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class WorkerState:
    worker_id: str
    worker_type: str
    status: str = "idle"
    assigned_topic: Optional[str] = None
    last_heartbeat_at: Optional[str] = None
    processed_count: int = 0
    error_count: int = 0
    governance_boundary: str = "bounded_no_unreviewed_external_action"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SignalEvent:
    event_id: str
    event_type: str
    topic: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    status: str = "new"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CampaignState:
    campaign_id: str
    name: str
    topics: List[str]
    status: str = "active"
    confidence: float = 0.0
    last_checkpoint_at: Optional[str] = None
    event_count: int = 0
    escalation_count: int = 0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EscalationDecision:
    escalation_id: str
    topic: str
    route: str
    reason: str
    confidence: float
    status: str = "requires_review"
    governance_boundary: str = "recommendation_only"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
""")

    write_file(LAYER / "worker_registry.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import WorkerState
from .models import utc_now


class WorkerRegistry:
    def __init__(self) -> None:
        self.workers: Dict[str, WorkerState] = {}

    def register(self, worker_type: str, assigned_topic: Optional[str] = None) -> WorkerState:
        seed = f"{worker_type}|{assigned_topic}|{len(self.workers)}"
        worker_id = "worker_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        worker = WorkerState(
            worker_id=worker_id,
            worker_type=worker_type,
            assigned_topic=assigned_topic,
            last_heartbeat_at=utc_now(),
        )
        self.workers[worker_id] = worker
        return worker

    def set_status(self, worker_id: str, status: str) -> None:
        self.workers[worker_id].status = status

    def record_success(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.processed_count += 1
        worker.status = "idle"
        worker.last_heartbeat_at = utc_now()

    def record_error(self, worker_id: str) -> None:
        worker = self.workers[worker_id]
        worker.error_count += 1
        worker.status = "error"
        worker.last_heartbeat_at = utc_now()

    def snapshot(self) -> List[dict]:
        return [worker.to_dict() for worker in self.workers.values()]
""")

    write_file(LAYER / "event_bus.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

from .models import SignalEvent


class SignalEventBus:
    def __init__(self) -> None:
        self.events: Dict[str, SignalEvent] = {}

    def publish(self, event_type: str, topic: str, payload: Optional[dict] = None, priority: int = 5) -> SignalEvent:
        seed = f"{event_type}|{topic}|{payload}|{len(self.events)}"
        event_id = "event_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
        event = SignalEvent(
            event_id=event_id,
            event_type=event_type,
            topic=topic,
            payload=payload or {},
            priority=priority,
        )
        self.events[event_id] = event
        return event

    def next_event(self) -> Optional[SignalEvent]:
        candidates = [event for event in self.events.values() if event.status == "new"]
        if not candidates:
            return None
        return sorted(candidates, key=lambda event: event.priority, reverse=True)[0]

    def mark_processing(self, event_id: str) -> None:
        self.events[event_id].status = "processing"

    def mark_done(self, event_id: str) -> None:
        self.events[event_id].status = "done"

    def snapshot(self) -> List[dict]:
        return [event.to_dict() for event in self.events.values()]
""")

    write_file(LAYER / "priority_router.py", """
from __future__ import annotations

from typing import Dict


class IngestionPriorityRouter:
    def score(self, signal: Dict[str, object]) -> int:
        confidence = float(signal.get("confidence", 0.5))
        novelty = float(signal.get("novelty", 0.5))
        urgency = float(signal.get("urgency", 0.5))
        contradiction = float(signal.get("contradiction", 0.0))

        raw = (confidence * 3.0) + (novelty * 2.0) + (urgency * 3.0) + (contradiction * 2.0)
        return max(1, min(10, round(raw)))

    def route(self, signal: Dict[str, object]) -> Dict[str, object]:
        priority = self.score(signal)

        if priority >= 8:
            route = "immediate_review_queue"
        elif priority >= 5:
            route = "standard_ingestion_queue"
        else:
            route = "low_priority_observation_queue"

        return {
            "priority": priority,
            "route": route,
            "reason": "Priority combines confidence, novelty, urgency, and contradiction pressure.",
        }
""")

    write_file(LAYER / "heartbeat_monitor.py", """
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List


class HeartbeatMonitor:
    def assess(self, workers: List[dict]) -> Dict[str, object]:
        stale = []
        healthy = []

        for worker in workers:
            heartbeat = worker.get("last_heartbeat_at")
            if not heartbeat:
                stale.append(worker.get("worker_id"))
                continue

            try:
                dt = datetime.fromisoformat(str(heartbeat).replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
            except Exception:
                age_seconds = 999999

            if age_seconds > 300:
                stale.append(worker.get("worker_id"))
            else:
                healthy.append(worker.get("worker_id"))

        return {
            "healthy_workers": healthy,
            "stale_workers": stale,
            "status": "healthy" if not stale else "attention_required",
        }
""")

    write_file(LAYER / "runtime_supervisor.py", """
from __future__ import annotations

from typing import Dict

from .event_bus import SignalEventBus
from .heartbeat_monitor import HeartbeatMonitor
from .worker_registry import WorkerRegistry


class RuntimeSupervisor:
    def __init__(self, workers: WorkerRegistry, bus: SignalEventBus) -> None:
        self.workers = workers
        self.bus = bus
        self.heartbeat = HeartbeatMonitor()

    def tick(self) -> Dict[str, object]:
        worker_snapshot = self.workers.snapshot()
        heartbeat = self.heartbeat.assess(worker_snapshot)

        event = self.bus.next_event()
        if event is None:
            return {
                "status": "idle",
                "heartbeat": heartbeat,
                "processed_event": None,
                "boundary": "supervisor does not perform unreviewed external action",
            }

        available = [worker for worker in self.workers.workers.values() if worker.status == "idle"]
        if not available:
            return {
                "status": "no_available_worker",
                "heartbeat": heartbeat,
                "processed_event": None,
            }

        worker = available[0]
        self.workers.set_status(worker.worker_id, "processing")
        self.bus.mark_processing(event.event_id)

        # Foundation-only processing. Real ingestion is delegated through governed adapters.
        self.bus.mark_done(event.event_id)
        self.workers.record_success(worker.worker_id)

        return {
            "status": "processed",
            "worker_id": worker.worker_id,
            "event_id": event.event_id,
            "topic": event.topic,
            "heartbeat": heartbeat,
            "boundary": "bounded internal orchestration only",
        }
""")

    write_file(LAYER / "state_recovery.py", """
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


class StateRecoveryManager:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("data") / "continuous_autonomous_intelligence" / "checkpoints"
        self.root.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, name: str, state: Dict[str, object]) -> Path:
        path = self.root / f"{name}.json"
        path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def load_checkpoint(self, name: str) -> Dict[str, object]:
        path = self.root / f"{name}.json"
        if not path.exists():
            return {"status": "missing", "name": name}
        return json.loads(path.read_text(encoding="utf-8"))

    def list_checkpoints(self) -> list[str]:
        return sorted(path.name for path in self.root.glob("*.json"))
""")

    write_file(LAYER / "campaign_continuity.py", """
from __future__ import annotations

import hashlib
from typing import Dict, List

from .models import CampaignState
from .models import utc_now


class CampaignContinuityManager:
    def __init__(self) -> None:
        self.campaigns: Dict[str, CampaignState] = {}

    def create_campaign(self, name: str, topics: List[str], confidence: float = 0.5) -> CampaignState:
        campaign_id = "campaign_" + hashlib.sha256(f"{name}|{topics}".encode("utf-8")).hexdigest()[:12]
        campaign = CampaignState(
            campaign_id=campaign_id,
            name=name,
            topics=topics,
            confidence=max(0.0, min(1.0, confidence)),
            last_checkpoint_at=utc_now(),
        )
        self.campaigns[campaign_id] = campaign
        return campaign

    def record_event(self, campaign_id: str) -> None:
        campaign = self.campaigns[campaign_id]
        campaign.event_count += 1
        campaign.last_checkpoint_at = utc_now()

    def record_escalation(self, campaign_id: str) -> None:
        campaign = self.campaigns[campaign_id]
        campaign.escalation_count += 1
        campaign.last_checkpoint_at = utc_now()

    def snapshot(self) -> List[dict]:
        return [campaign.to_dict() for campaign in self.campaigns.values()]
""")

    write_file(LAYER / "conflict_reconciliation.py", """
from __future__ import annotations

from typing import Dict, List


class SignalConflictReconciler:
    def reconcile(self, evidence_packets: List[Dict[str, object]]) -> Dict[str, object]:
        supporting = [item for item in evidence_packets if item.get("stance") == "supporting"]
        conflicting = [item for item in evidence_packets if item.get("stance") == "conflicting"]
        neutral = [item for item in evidence_packets if item.get("stance") not in {"supporting", "conflicting"}]

        support_score = sum(float(item.get("confidence", 0.5)) for item in supporting)
        conflict_score = sum(float(item.get("confidence", 0.5)) for item in conflicting)

        if conflict_score > support_score:
            status = "conflict_dominant"
        elif support_score > conflict_score:
            status = "support_dominant"
        else:
            status = "balanced_or_insufficient"

        return {
            "status": status,
            "supporting_count": len(supporting),
            "conflicting_count": len(conflicting),
            "neutral_count": len(neutral),
            "support_score": round(support_score, 4),
            "conflict_score": round(conflict_score, 4),
            "recommendation": "escalate_for_review" if conflict_score > 0 else "continue_monitoring",
        }
""")

    write_file(LAYER / "escalation_contracts.py", """
from __future__ import annotations

import hashlib
from typing import Dict

from .models import EscalationDecision


class EventDrivenEscalationEngine:
    def evaluate(self, topic: str, priority: int, conflict_status: str, confidence: float) -> EscalationDecision:
        if conflict_status == "conflict_dominant":
            route = "human_review"
            reason = "Conflicting evidence dominates supporting evidence."
        elif priority >= 8 and confidence >= 0.7:
            route = "strategic_decision_layer"
            reason = "High-priority, high-confidence signal qualifies for decisioning."
        elif priority >= 6:
            route = "continued_monitoring"
            reason = "Signal is meaningful but requires more evidence."
        else:
            route = "archive_observation"
            reason = "Signal does not currently justify escalation."

        escalation_id = "escalation_" + hashlib.sha256(f"{topic}|{route}|{reason}".encode("utf-8")).hexdigest()[:12]

        return EscalationDecision(
            escalation_id=escalation_id,
            topic=topic,
            route=route,
            reason=reason,
            confidence=max(0.0, min(1.0, confidence)),
            status="requires_review" if route in {"human_review", "strategic_decision_layer"} else "bounded",
        )
""")

    write_file(LAYER / "continuous_regression_lock.py", """
from __future__ import annotations

from typing import Dict, List


class ContinuousIntelligenceRegressionLock:
    def validate(self, output: Dict[str, object]) -> Dict[str, object]:
        errors: List[str] = []
        warnings: List[str] = []

        if output.get("layer") != "continuous_autonomous_intelligence":
            errors.append("Invalid layer marker.")

        if output.get("governance_boundary") != "bounded_internal_orchestration_no_unreviewed_external_action":
            errors.append("Governance boundary missing or invalid.")

        required = ["workers", "events", "supervisor_tick", "campaigns", "escalation"]
        for key in required:
            if key not in output:
                errors.append(f"Missing required output key: {key}")

        escalation = output.get("escalation", {})
        if isinstance(escalation, dict) and escalation.get("status") == "requires_review":
            warnings.append("Escalation requires user/operator review before downstream action.")

        return {
            "version": "v17.30",
            "regression_status": "passed" if not errors else "failed",
            "errors": errors,
            "warnings": warnings,
            "checks": {
                "worker_registry_present": "workers" in output,
                "event_bus_present": "events" in output,
                "supervisor_present": "supervisor_tick" in output,
                "state_recovery_present": "checkpoint" in output,
                "bounded_external_action": output.get("governance_boundary") == "bounded_internal_orchestration_no_unreviewed_external_action",
            },
        }
""")

    write_file(LAYER / "runtime.py", """
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .campaign_continuity import CampaignContinuityManager
from .conflict_reconciliation import SignalConflictReconciler
from .continuous_regression_lock import ContinuousIntelligenceRegressionLock
from .escalation_contracts import EventDrivenEscalationEngine
from .event_bus import SignalEventBus
from .priority_router import IngestionPriorityRouter
from .runtime_supervisor import RuntimeSupervisor
from .state_recovery import StateRecoveryManager
from .worker_registry import WorkerRegistry


class ContinuousAutonomousIntelligenceRuntime:
    def __init__(self, checkpoint_root: Path | None = None) -> None:
        self.workers = WorkerRegistry()
        self.bus = SignalEventBus()
        self.router = IngestionPriorityRouter()
        self.campaigns = CampaignContinuityManager()
        self.reconciler = SignalConflictReconciler()
        self.escalator = EventDrivenEscalationEngine()
        self.recovery = StateRecoveryManager(checkpoint_root)
        self.regression = ContinuousIntelligenceRegressionLock()
        self.supervisor = RuntimeSupervisor(self.workers, self.bus)

    def run_cycle(
        self,
        campaign_name: str,
        topics: List[str],
        signal: Dict[str, object],
        evidence_packets: List[Dict[str, object]] | None = None,
    ) -> Dict[str, Any]:
        campaign = self.campaigns.create_campaign(
            name=campaign_name,
            topics=topics,
            confidence=float(signal.get("confidence", 0.5)),
        )

        worker = self.workers.register("bounded_ingestion_worker", assigned_topic=topics[0] if topics else None)
        route = self.router.route(signal)

        event = self.bus.publish(
            event_type="signal_observed",
            topic=str(signal.get("topic") or (topics[0] if topics else "unknown")),
            payload=signal,
            priority=int(route["priority"]),
        )
        self.campaigns.record_event(campaign.campaign_id)

        supervisor_tick = self.supervisor.tick()
        reconciliation = self.reconciler.reconcile(evidence_packets or [])

        escalation = self.escalator.evaluate(
            topic=event.topic,
            priority=int(route["priority"]),
            conflict_status=str(reconciliation["status"]),
            confidence=float(signal.get("confidence", 0.5)),
        )

        if escalation.route in {"strategic_decision_layer", "human_review"}:
            self.campaigns.record_escalation(campaign.campaign_id)

        state = {
            "campaigns": self.campaigns.snapshot(),
            "workers": self.workers.snapshot(),
            "events": self.bus.snapshot(),
            "route": route,
            "reconciliation": reconciliation,
            "escalation": escalation.to_dict(),
        }
        checkpoint_path = self.recovery.save_checkpoint(campaign.campaign_id, state)

        output: Dict[str, Any] = {
            "layer": "continuous_autonomous_intelligence",
            "versions": {
                "worker_registry": "v17.21",
                "event_bus": "v17.22",
                "priority_router": "v17.23",
                "runtime_supervisor": "v17.24",
                "heartbeat_monitor": "v17.25",
                "state_recovery": "v17.26",
                "campaign_continuity": "v17.27",
                "conflict_reconciliation": "v17.28",
                "event_driven_escalation": "v17.29",
                "continuous_regression_lock": "v17.30",
            },
            "governance_boundary": "bounded_internal_orchestration_no_unreviewed_external_action",
            "campaigns": self.campaigns.snapshot(),
            "workers": self.workers.snapshot(),
            "events": self.bus.snapshot(),
            "route": route,
            "supervisor_tick": supervisor_tick,
            "reconciliation": reconciliation,
            "escalation": escalation.to_dict(),
            "checkpoint": str(checkpoint_path),
        }

        output["regression"] = self.regression.validate(output)
        return output
""")

    write_file(TESTS / "test_continuous_autonomous_intelligence.py", """
from pathlib import Path

from claire.continuous_autonomous_intelligence import ContinuousAutonomousIntelligenceRuntime


def test_continuous_cycle_passes_regression(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="AI infrastructure monitoring",
        topics=["governed research systems"],
        signal={
            "topic": "governed research systems",
            "confidence": 0.76,
            "novelty": 0.7,
            "urgency": 0.8,
            "contradiction": 0.2,
        },
        evidence_packets=[
            {"stance": "supporting", "confidence": 0.7},
            {"stance": "supporting", "confidence": 0.6},
        ],
    )

    assert result["layer"] == "continuous_autonomous_intelligence"
    assert result["regression"]["regression_status"] == "passed"
    assert result["supervisor_tick"]["status"] == "processed"
    assert result["governance_boundary"] == "bounded_internal_orchestration_no_unreviewed_external_action"


def test_conflict_dominant_routes_to_review(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="conflict test",
        topics=["market signal"],
        signal={
            "topic": "market signal",
            "confidence": 0.62,
            "novelty": 0.5,
            "urgency": 0.5,
            "contradiction": 0.9,
        },
        evidence_packets=[
            {"stance": "conflicting", "confidence": 0.9},
            {"stance": "supporting", "confidence": 0.2},
        ],
    )

    assert result["reconciliation"]["status"] == "conflict_dominant"
    assert result["escalation"]["route"] == "human_review"
    assert result["regression"]["regression_status"] == "passed"


def test_checkpoint_is_written(tmp_path: Path):
    runtime = ContinuousAutonomousIntelligenceRuntime(checkpoint_root=tmp_path)
    result = runtime.run_cycle(
        campaign_name="checkpoint test",
        topics=["signal"],
        signal={"topic": "signal", "confidence": 0.5},
    )

    assert Path(result["checkpoint"]).exists()
""")

    write_file(DOCS / "v17_21_to_v17_30_continuous_autonomous_intelligence.md", """
# Claire v17.21-v17.30 Continuous Autonomous Intelligence Infrastructure

This build moves Claire from runtime-capable governed connectivity toward continuously operating governed intelligence infrastructure.

## Included Builds

- v17.21 Worker Registry
- v17.22 Signal Event Bus
- v17.23 Ingestion Priority Router
- v17.24 Runtime Supervisor
- v17.25 Heartbeat Monitor
- v17.26 State Recovery Manager
- v17.27 Campaign Continuity Manager
- v17.28 Signal Conflict Reconciler
- v17.29 Event-Driven Escalation Contracts
- v17.30 Continuous Intelligence Regression Lock

## Governance Boundary

This layer performs bounded internal orchestration only.

It does not:
- perform unreviewed external actions
- bypass source policy
- execute autonomous real-world operations
- make unrestricted internet decisions

It creates the continuity, worker, event, recovery, and escalation substrate needed for future production-scale monitoring.
""")

    write_json(DATA / "continuous_autonomous_intelligence_manifest.json", {
        "installed_at": utc_now(),
        "layer": "continuous_autonomous_intelligence",
        "version_range": "v17.21-v17.30",
        "status": "installed",
        "governance_boundary": "bounded_internal_orchestration_no_unreviewed_external_action",
        "capabilities": [
            "worker_registry",
            "signal_event_bus",
            "ingestion_priority_routing",
            "runtime_supervisor",
            "heartbeat_monitor",
            "state_recovery",
            "campaign_continuity",
            "signal_conflict_reconciliation",
            "event_driven_escalation_contracts",
            "continuous_regression_lock",
        ],
        "not_included_yet": [
            "distributed_cloud_worker_pool",
            "production_message_broker",
            "live_streaming_market_feeds",
            "browser_automation",
            "unrestricted_external_actions",
            "self_modifying_runtime"
        ],
        "tests": [
            "tests/continuous_autonomous_intelligence/test_continuous_autonomous_intelligence.py"
        ],
    })

    print("")
    print("INSTALL COMPLETE: Claire v17.21-v17.30 Continuous Autonomous Intelligence Infrastructure")
    print("")
    print("Run tests with:")
    print("    python -m pytest tests/continuous_autonomous_intelligence -q")
    print("")
    print("Optional smoke test:")
    print("    python -c \"from claire.continuous_autonomous_intelligence import ContinuousAutonomousIntelligenceRuntime; print(ContinuousAutonomousIntelligenceRuntime().run_cycle('test',['ai'],{'topic':'ai','confidence':0.7})['regression']['regression_status'])\"")


if __name__ == "__main__":
    main()
