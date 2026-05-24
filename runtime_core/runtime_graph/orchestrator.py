from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _score_terms(text: str, terms: List[str]) -> int:
    low = text.lower()
    return sum(1 for term in terms if term in low)


@dataclass
class RuntimeGraphDecision:
    run_id: str
    status: str
    mode: str
    route: str
    terminal_state: str
    confidence: float
    governance_state: str
    stage_status: List[Dict[str, Any]]
    evidence: Dict[str, Any]
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "mode": self.mode,
            "route": self.route,
            "terminal_state": self.terminal_state,
            "confidence": self.confidence,
            "governance_state": self.governance_state,
            "stage_status": self.stage_status,
            "evidence": self.evidence,
            "reasons": self.reasons,
            "created_at": _now(),
        }


class RuntimeGraphOrchestrator:
    """Small, honest route graph layer.

    This does not replace Claire's deeper evaluation engine.
    It provides a canonical graph decision contract so cockpit/runtime payloads
    can stop drifting away from backend truth.
    """

    STAGES = [
        "Signal Ingestion",
        "Signal Normalization",
        "Source Validation & Weighting",
        "Context Expansion",
        "Signal Consolidation",
        "Entity Extraction",
        "Relationship Mapping",
        "Trend Discovery",
        "Cluster Formation",
        "Insight / Thesis Structuring",
        "Gap Detection",
        "Gap Qualification",
        "Discovery Generation",
        "Breakthrough Identification & Classification",
        "Advancement Path Selection",
        "Auto Invention / Solution Generation",
        "Solution Structuring",
        "Buildability Assessment",
        "Viability Assessment",
        "Manufacturability / Deployability Assessment",
        "Feasibility Validation",
        "Design Portal Output / Blueprints / Specs",
        "Market Positioning",
        "Moat & Differentiation",
        "Business Model & Value Capture",
        "Competitor Analysis",
        "Portfolio Creation / Optimization",
        "Acquirer Identification",
        "Acquisition Fit & Rationale",
        "Final Package Construction",
    ]

    def decide_route(self, raw_input: str, mode: str = "deterministic") -> Dict[str, Any]:
        text = (raw_input or "").strip()
        run_id = "graph-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

        if not text:
            return RuntimeGraphDecision(
                run_id=run_id,
                status="blocked",
                mode=mode,
                route="none",
                terminal_state="insufficient_data",
                confidence=0.0,
                governance_state="blocked",
                stage_status=self._stage_status([], skipped_reason="missing raw_input"),
                evidence={"input_length": 0, "reason": "raw_input is required"},
                reasons=["raw_input is empty"],
            ).to_dict()

        breakthrough_terms = [
            "breakthrough", "patent", "novel", "invention", "design", "blueprint",
            "manufacturability", "buildability", "prototype", "system replacement",
            "autonomous", "constraints", "feasibility"
        ]
        acquisition_terms = [
            "acquisition", "acquirer", "strategic buyer", "m&a", "deal",
            "moat", "value capture", "market entry"
        ]
        portfolio_terms = [
            "portfolio", "risk", "exposure", "allocation", "optimization",
            "market", "trend", "thesis", "sector", "asset"
        ]

        b = _score_terms(text, breakthrough_terms)
        a = _score_terms(text, acquisition_terms)
        p = _score_terms(text, portfolio_terms)

        if b >= max(a, p) and b >= 2:
            route = "breakthrough_system_transformation"
            active = list(range(1, 31))
            terminal = "breakthrough_route_selected"
            reasons = ["breakthrough/design/system-transformation signals crossed route threshold"]
        elif a >= max(b, p) and a >= 2:
            route = "acquisition_intelligence"
            active = [1,2,3,4,5,6,7,8,9,10,24,25,28,29,30]
            terminal = "acquisition_route_selected"
            reasons = ["acquisition/deal/moat signals crossed route threshold"]
        else:
            route = "portfolio_intelligence"
            active = [1,2,3,4,5,6,7,8,9,10,23,26,27]
            terminal = "portfolio_route_selected"
            reasons = ["default trend/thesis/portfolio path selected"]

        total = max(1, b + a + p)
        confidence = round(min(0.92, 0.42 + 0.06 * total), 4)

        return RuntimeGraphDecision(
            run_id=run_id,
            status="success",
            mode=mode,
            route=route,
            terminal_state=terminal,
            confidence=confidence,
            governance_state="ready",
            stage_status=self._stage_status(active),
            evidence={
                "input_length": len(text),
                "scores": {
                    "breakthrough_terms": b,
                    "acquisition_terms": a,
                    "portfolio_terms": p,
                },
                "route_decision_basis": "keyword route graph contract; deeper scorer may override in full evaluate pipeline",
            },
            reasons=reasons,
        ).to_dict()

    def _stage_status(self, active_numbers: List[int], skipped_reason: str = "skipped_by_route") -> List[Dict[str, Any]]:
        active = set(active_numbers)
        rows = []
        for idx, name in enumerate(self.STAGES, start=1):
            if idx in active:
                status = "selected"
                reason = None
            else:
                status = "skipped"
                reason = skipped_reason
            rows.append({"stage": idx, "name": name, "status": status, "reason": reason})
        return rows
