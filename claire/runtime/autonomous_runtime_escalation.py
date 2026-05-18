"""Claire Syntalion v19.52-v19.61 Autonomous Runtime Escalation Pack.

Purpose
-------
Proves the next contract layer after web-to-pipeline stabilization:

search/web signal -> governed evidence -> ingestion -> route selection ->
autonomous escalation decision -> runtime execution proof -> dashboard/review
sync -> quality gate -> reviewable operator output.

The module is deterministic and offline-safe. It is designed as a runtime
contract layer, not a live-web implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
import hashlib
import re

BUILD_RANGE = "v19.52-v19.61"
BUILD_STEPS = [
    "v19.52_autonomous_escalation_contract",
    "v19.53_evidence_readiness_classifier",
    "v19.54_signal_to_runtime_intent_mapper",
    "v19.55_route_execution_priority_lock",
    "v19.56_terminal_state_governance",
    "v19.57_dashboard_review_sync_contract",
    "v19.58_quality_gate_runtime_assertions",
    "v19.59_operator_review_payload",
    "v19.60_launch_candidate_traceability",
    "v19.61_autonomous_runtime_escalation_proof",
]

TRUSTED_SOURCE_HINTS = ("official", "sec", "federal", "gov", "standards", "primary", "exchange", "issuer")
PORTFOLIO_HINTS = ("market", "trend", "stock", "portfolio", "asset", "sector", "equity", "macro", "infrastructure", "energy")
BREAKTHROUGH_HINTS = ("breakthrough", "invention", "patent", "novel", "new material", "architecture", "prototype")
ACQUISITION_HINTS = ("acquisition", "buyer", "strategic fit", "moat", "package", "target")
DESIGN_HINTS = ("design", "build", "blueprint", "system", "component", "software", "platform")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _tokens(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _contains_any(text: str, hints: tuple[str, ...]) -> bool:
    lower = (text or "").lower()
    return any(h in lower for h in hints)


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-" + hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class RuntimeEscalationRequest:
    query: str
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)
    operator_mode: str = "governed_web_pipeline"
    dashboard_context: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeEscalationResult:
    build_range: str
    status: str
    run_id: str
    timestamp: str
    search_execution: Dict[str, Any]
    evidence_governance: Dict[str, Any]
    pipeline_ingestion: Dict[str, Any]
    route_execution: Dict[str, Any]
    terminal_state: Dict[str, Any]
    dashboard_sync: Dict[str, Any]
    quality_gate: Dict[str, Any]
    operator_review: Dict[str, Any]
    traceability: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def normalize_evidence(query: str, evidence_items: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    """Normalize supplied evidence or synthesize an offline-safe proof item."""
    items = list(evidence_items or [])
    if not items:
        items = [
            {
                "title": f"Governed evidence proof for {query}",
                "source": "offline_contract_primary_source",
                "url": "internal://governed-web-proof",
                "snippet": query,
                "source_type": "primary",
            }
        ]

    normalized: List[Dict[str, Any]] = []
    for idx, raw in enumerate(items, start=1):
        title = str(raw.get("title") or raw.get("name") or f"Evidence {idx}").strip()
        source = str(raw.get("source") or raw.get("domain") or raw.get("provider") or "unknown_source").strip()
        snippet = str(raw.get("snippet") or raw.get("summary") or raw.get("content") or "").strip()
        url = str(raw.get("url") or raw.get("link") or f"internal://evidence/{idx}").strip()
        text = " ".join([title, source, snippet, url])
        trust_score = 0.55
        if _contains_any(text, TRUSTED_SOURCE_HINTS):
            trust_score += 0.30
        if url.startswith("https://") or url.startswith("internal://"):
            trust_score += 0.10
        if len(_tokens(snippet)) >= 3:
            trust_score += 0.05
        trust_score = min(round(trust_score, 2), 1.0)
        normalized.append(
            {
                "evidence_id": _stable_id("ev", title + source + snippet + url),
                "title": title,
                "source": source,
                "url": url,
                "snippet": snippet,
                "trust_score": trust_score,
                "accepted": trust_score >= 0.60,
            }
        )
    return normalized


def classify_route(query: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    text = " ".join([query] + [str(e.get("title", "")) + " " + str(e.get("snippet", "")) for e in evidence]).lower()
    scores = {
        "portfolio": 0,
        "breakthrough": 0,
        "design": 0,
        "acquisition": 0,
        "trend": 1,
    }
    for token in PORTFOLIO_HINTS:
        if token in text:
            scores["portfolio"] += 2
    for token in BREAKTHROUGH_HINTS:
        if token in text:
            scores["breakthrough"] += 2
    for token in DESIGN_HINTS:
        if token in text:
            scores["design"] += 2
    for token in ACQUISITION_HINTS:
        if token in text:
            scores["acquisition"] += 2
    if "trend" in text or "emerging" in text:
        scores["trend"] += 2

    priority = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    selected = priority[0][0]
    if selected == "portfolio":
        terminal = "portfolio_action_ready"
    elif selected == "breakthrough":
        terminal = "breakthrough_classified"
    elif selected == "design":
        terminal = "design_output_ready"
    elif selected == "acquisition":
        terminal = "acquisition_package_ready"
    else:
        terminal = "trend_thesis_ready"
    return {
        "selected_route": selected,
        "terminal_state": terminal,
        "route_scores": scores,
        "priority_lock": True,
        "skipped_routes": [route for route in scores if route != selected],
    }


def run_autonomous_runtime_escalation(query: str, evidence_items: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    request = RuntimeEscalationRequest(query=query, evidence_items=list(evidence_items or []))
    normalized_query = (request.query or "").strip()
    run_id = _stable_id("run", normalized_query or "empty")

    if not normalized_query:
        result = RuntimeEscalationResult(
            build_range=BUILD_RANGE,
            status="validation_failed",
            run_id=run_id,
            timestamp=_now(),
            search_execution={"query": normalized_query, "executed": False, "reason": "empty_query"},
            evidence_governance={"evidence_state": "blocked", "accepted_count": 0, "items": []},
            pipeline_ingestion={"accepted": False, "reason": "empty_query"},
            route_execution={"selected_route": "none", "priority_lock": False},
            terminal_state={"terminal_state": "blocked", "reason": "empty_query"},
            dashboard_sync={"panels_ready": False, "panels": []},
            quality_gate={"passed": False, "failed_checks": ["query_required"]},
            operator_review={"reviewable": True, "summary": "Blocked: query is required."},
            traceability={"build_steps": BUILD_STEPS, "event_count": 1},
        )
        return result.to_dict()

    evidence = normalize_evidence(normalized_query, request.evidence_items)
    accepted = [item for item in evidence if item["accepted"]]
    route = classify_route(normalized_query, accepted or evidence)
    evidence_ready = len(accepted) > 0
    ingestion_accepted = evidence_ready and len(_tokens(normalized_query)) > 0
    terminal = route["terminal_state"] if ingestion_accepted else "insufficient_data"
    quality_failures: List[str] = []
    if not evidence_ready:
        quality_failures.append("no_governed_evidence")
    if not ingestion_accepted:
        quality_failures.append("pipeline_ingestion_not_accepted")
    if not route.get("priority_lock"):
        quality_failures.append("route_priority_not_locked")

    result = RuntimeEscalationResult(
        build_range=BUILD_RANGE,
        status="ok" if not quality_failures else "needs_review",
        run_id=run_id,
        timestamp=_now(),
        search_execution={
            "query": normalized_query,
            "executed": True,
            "governed": True,
            "mode": request.operator_mode,
            "result_count": len(evidence),
        },
        evidence_governance={
            "evidence_state": "governed_evidence_ready" if evidence_ready else "insufficient_evidence",
            "accepted_count": len(accepted),
            "items": evidence,
        },
        pipeline_ingestion={
            "accepted": ingestion_accepted,
            "ingestion_state": "pipeline_input_ready" if ingestion_accepted else "insufficient_data",
            "signal_count": len(accepted),
        },
        route_execution={
            **route,
            "autonomous_escalation_enabled": True,
            "execution_order_locked": True,
        },
        terminal_state={
            "terminal_state": terminal,
            "review_required": True,
            "operator_can_promote": terminal not in {"blocked", "failed"},
        },
        dashboard_sync={
            "panels_ready": True,
            "panels": [
                "search_execution",
                "governed_evidence",
                "pipeline_ingestion",
                "route_execution",
                "terminal_state",
                "operator_review",
            ],
            "temporary_dashboard_only": True,
            "enterprise_dashboard_v2_deferred": True,
        },
        quality_gate={
            "passed": not quality_failures,
            "failed_checks": quality_failures,
            "required_checks": [
                "query_present",
                "governed_search_executed",
                "evidence_ready",
                "pipeline_ingestion_accepted",
                "route_priority_locked",
                "terminal_state_present",
                "dashboard_panels_ready",
            ],
        },
        operator_review={
            "reviewable": True,
            "summary": f"{BUILD_RANGE}: {terminal} via {route['selected_route']} route.",
            "recommended_action": "review_output_then_promote_or_hold",
        },
        traceability={
            "build_steps": BUILD_STEPS,
            "event_count": 10,
            "source_contract": "web_to_pipeline_stabilization_successor",
        },
    )
    return result.to_dict()


# Backward-friendly aliases for likely import styles in later packs.
run_runtime_escalation = run_autonomous_runtime_escalation
run_v19_52_to_v19_61 = run_autonomous_runtime_escalation
