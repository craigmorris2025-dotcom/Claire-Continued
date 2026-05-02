"""Live opportunity monitor pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from claire.live_intelligence.connectors import ConnectorRunner
from claire.live_intelligence.entity_registry import SourceEntityRegistry
from claire.live_intelligence.gap_detection import GapDetectionEngine
from claire.live_intelligence.signal_extraction import SignalExtractionWorker
from claire.live_intelligence.solution_synthesis import SolutionSynthesisEngine
from claire.live_intelligence.trend_clustering import TrendClusterer


class LiveOpportunityMonitor:
    """Run the live intelligence chain from source entities to solution candidates."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.registry = SourceEntityRegistry(project_root)
        self.connectors = ConnectorRunner(project_root)
        self.extractor = SignalExtractionWorker()
        self.clusterer = TrendClusterer()
        self.gaps = GapDetectionEngine()
        self.synthesizer = SolutionSynthesisEngine()

    def status(self) -> Dict[str, Any]:
        registry_status = self.registry.status()
        connector_status = self.connectors.status()
        return {
            "status": "success",
            "monitor": "live_opportunity_monitor_v1",
            "registry_version": registry_status.get("registry_version"),
            "entity_count": registry_status.get("entity_count"),
            "connector_count": connector_status.get("connector_count"),
            "pipeline": [
                "source_entity_registry",
                "source_specific_connectors",
                "signal_extraction_workers",
                "signal_clustering_trend_formation",
                "gap_detection",
                "solution_synthesis",
                "live_opportunity_monitor",
            ],
            "ready": registry_status.get("entity_count", 0) > 0 and connector_status.get("connector_count", 0) >= 4,
        }

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        connector_payload = self.connectors.run(payload)
        extracted = self.extractor.extract(connector_payload, context=payload)
        clusters = self.clusterer.cluster(extracted)
        gaps = self.gaps.detect(clusters)
        solutions = self.synthesizer.synthesize(gaps, context=payload)
        ready = bool(solutions.get("candidates"))
        return {
            "status": "success" if ready else "no_candidates",
            "monitor": "live_opportunity_monitor_v1",
            "connectors": connector_payload,
            "extracted": extracted,
            "clusters": clusters,
            "gaps": gaps,
            "solutions": solutions,
            "live_opportunities_ready": ready,
            "top_candidate": (solutions.get("candidates") or [None])[0],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
