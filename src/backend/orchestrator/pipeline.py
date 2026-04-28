"""
Pipeline Orchestrator — runs the full 6-phase, 24-engine evaluation.
Wires together: Contract → Orreadir → Semantic → Engines → Scoring → Bridge → Persist.
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from backend.claire.contract import ClaireIntent, ClaireResult, PlanObject, SemanticRepresentation
from backend.claire.orreadir import OrreadirRouter
from backend.claire.interpreter import Interpreter
from backend.core.planner import Planner
from backend.core.semantic import SemanticLayer
from backend.core.data_engine import DataEngine
from backend.engines import DOMAIN_REGISTRY, PHASE_SEQUENCE
from backend.scoring.calibrator import ScoreCalibrator
from backend.connectors.manager import ConnectorManager
from backend.persistence.database import Database
from backend.bridge.masterpass import MasterPassBridge
from backend.orchestrator.pattern_recognition import PatternRecognizer
from backend.orchestrator.fettio import FeTTiom
from backend.orchestrator.desking import Desking

logger = logging.getLogger("claire.orchestrator.pipeline")


class PipelineOrchestrator:
    """Full pipeline: 6 phases, 24 engines, end-to-end."""

    def __init__(self):
        self.router = OrreadirRouter()
        self.planner = Planner()
        self.semantic = SemanticLayer()
        self.data_engine = DataEngine()
        self.calibrator = ScoreCalibrator()
        self.connector_mgr = ConnectorManager()
        self.interpreter = Interpreter()
        self.bridge = MasterPassBridge()
        self.pattern_recognizer = PatternRecognizer()
        self.fettio = FeTTiom()
        self.desking = Desking()
        self.db = Database()

    def execute(self, intent: ClaireIntent) -> ClaireResult:
        """Execute the full pipeline for a validated intent."""
        started = datetime.utcnow().isoformat()
        run_id = f"run-{uuid.uuid4().hex[:6]}"

        logger.info(f"Pipeline {run_id} starting: mode={intent.mode}, "
                     f"input={len(intent.raw_input)} chars")

        # 1. Route
        route_decision = self.router.route(intent)

        # 2. Plan
        plan = self.planner.create_plan(intent)

        # 3. Semantic / NLP
        sem = self.semantic.process(intent.raw_input)

        # 4. Build engine context
        context = {
            "raw_input": intent.raw_input,
            "mode": intent.mode,
            "intent_id": intent.id,
            "run_id": run_id,
            "domain_scores": sem.dimensions,
            "primary_domain": sem.domain,
            "keywords": sem.keywords,
            "entities": sem.entities,
            "semantic_confidence": sem.confidence,
        }

        # 5. Fetch connector data — all modes get data (deterministic uses local fallback)
        connector_query = {
            "sector": sem.domain,
            "domain": sem.domain,
            "keywords": sem.keywords,
        }
        connector_data = self.connector_mgr.fetch_all(connector_query, mode=intent.mode)
        context["connector_data"] = connector_data

        # 6. Run all 24 engines across 6 phases
        for phase_name, engine_keys in PHASE_SEQUENCE:
            for key in engine_keys:
                engine = DOMAIN_REGISTRY.get(key)
                if engine:
                    try:
                        context = engine.process(context)
                    except Exception as e:
                        logger.error(f"Engine {key} failed: {e}")
                        context[f"{key}_score"] = 0.0

        # 7. Pattern recognition (hybrid mode)
        if intent.mode == "hybrid":
            context = self.pattern_recognizer.analyze(context)
            context = self.fettio.process(context)
            context = self.desking.distribute(context)

        # 8. Calibrate scores
        raw_scores = {k: v for k, v in context.items()
                      if k.endswith("_score") and isinstance(v, (int, float))}
        calibrated = self.calibrator.calibrate(raw_scores)

        # 9. Build result
        result = ClaireResult(
            intent_id=intent.id,
            status="success",
            plan=plan,
            semantic=sem,
            mode=intent.mode,
            scores=calibrated,
            acquirer_matches=context.get("acquirer_matches", []),
            data={
                "run_id": run_id,
                "keywords": sem.keywords,
                "domain": sem.domain,
                "domain_scores": sem.dimensions,
                "engine_details": context.get("engine_details", {}),
                "connector_sources": {k: v.get("source", "unknown")
                                      for k, v in connector_data.items()
                                      if isinstance(v, dict)},
                "patterns": context.get("patterns", {}),
                "fettio_aggregate": context.get("fettio_aggregate", 0),
                "desking": context.get("desking_distributions", []),
            },
        )

        # 10. Interpret and classify
        result = self.interpreter.finalize(result)

        # 11. MasterPass bridge
        bridge_result = self.bridge.process(result)
        result.ready_for_syntalion = bridge_result.get("syntalion_ready", False)

        # 12. Persist
        try:
            self.db.save_run({
                "run_id": run_id,
                "mode": intent.mode,
                "input_text": intent.raw_input,
                "decision_score": calibrated.get("decision_score", 0),
                "decision_class": result.decision_classification,
                "breakthrough_score": calibrated.get("breakthrough_score", 0),
                "portfolio_score": calibrated.get("portfolio_score", 0),
                "confidence": calibrated.get("_confidence", 0),
                "started_at": started,
                "full_result": result.to_dict(),
            })
        except Exception as e:
            logger.error(f"DB save failed: {e}")

        logger.info(f"Pipeline {run_id} complete: decision={result.decision_classification}, "
                     f"breakthrough={result.breakthrough_classification}")
        return result
