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
