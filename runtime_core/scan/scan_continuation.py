"""Bounded scan continuation for route-aware Claire outputs."""

from __future__ import annotations

from typing import Any, Callable, Dict, List


MAX_SCAN_ITERATIONS = 3
MIN_SIGNALS_FOR_TREND = 1
MIN_TREND_CONFIDENCE = 0.35
MIN_DISCOVERY_CONFIDENCE = 0.50
MIN_BREAKTHROUGH_CONFIDENCE = 0.70


class ScanContinuationRunner:
    """Continue scan passes until a useful terminal route condition exists."""

    def __init__(
        self,
        max_iterations: int = MAX_SCAN_ITERATIONS,
        min_signals_for_trend: int = MIN_SIGNALS_FOR_TREND,
        min_trend_confidence: float = MIN_TREND_CONFIDENCE,
        min_discovery_confidence: float = MIN_DISCOVERY_CONFIDENCE,
        min_breakthrough_confidence: float = MIN_BREAKTHROUGH_CONFIDENCE,
    ) -> None:
        self.max_iterations = max(1, int(max_iterations or MAX_SCAN_ITERATIONS))
        self.min_signals_for_trend = max(1, int(min_signals_for_trend or MIN_SIGNALS_FOR_TREND))
        self.min_trend_confidence = float(min_trend_confidence)
        self.min_discovery_confidence = float(min_discovery_confidence)
        self.min_breakthrough_confidence = float(min_breakthrough_confidence)

    def run_until_result(
        self,
        payload: Dict[str, Any],
        scan_once: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> Dict[str, Any]:
        iterations: List[Dict[str, Any]] = []
        terminal: Dict[str, Any] = {}
        last_result: Dict[str, Any] = {}
        base_payload = dict(payload or {})

        for index in range(1, self.max_iterations + 1):
            iteration_payload = dict(base_payload)
            iteration_payload["scan_iteration"] = index
            iteration_payload["prior_scan_iterations"] = iterations
            result = scan_once(iteration_payload) or {}
            last_result = result
            progress = self.evaluate_scan_progress(result, index)
            iterations.append(progress)
            terminal = self._terminal(progress, index)
            if terminal.get("terminal"):
                break

            base_payload["scan_enrichment_context"] = self._enrichment_context(iterations, result)

        if not terminal.get("terminal"):
            terminal = {
                "terminal": True,
                "terminal_state": "max_iterations_reached",
                "terminal_reason": f"Reached max scan iterations ({self.max_iterations}) before discovery or insufficient-data resolution.",
                "route_selected": "insufficient_data_output",
            }

        return {
            "status": "success" if terminal.get("terminal_state") not in {"blocked", "failed"} else terminal.get("terminal_state"),
            "terminal_state": terminal.get("terminal_state"),
            "terminal_reason": terminal.get("terminal_reason"),
            "route_selected": terminal.get("route_selected"),
            "scan_iterations": iterations,
            "last_result": last_result,
            "max_iterations": self.max_iterations,
            "thresholds": {
                "min_signals_for_trend": self.min_signals_for_trend,
                "min_trend_confidence": self.min_trend_confidence,
                "min_discovery_confidence": self.min_discovery_confidence,
                "min_breakthrough_confidence": self.min_breakthrough_confidence,
            },
        }

    def evaluate_scan_progress(self, result: Dict[str, Any], index: int) -> Dict[str, Any]:
        status = str(result.get("status") or "")
        signals_found = self._int(self._get(result, "extracted.signal_count", 0))
        connector_records = self._int(self._get(result, "connectors.record_count", 0))
        cluster_count = self._int(self._get(result, "clusters.cluster_count", 0))
        gap_count = self._int(self._get(result, "gaps.gap_count", 0))
        solutions = result.get("solutions", {}).get("candidates", []) if isinstance(result.get("solutions"), dict) else []
        solution_count = len(solutions) if isinstance(solutions, list) else 0
        activated_count = len(result.get("activated_candidates") or [])

        signal_base = max(signals_found, connector_records)
        trend_confidence = min(0.95, (signal_base * 0.20) + (cluster_count * 0.25))
        discovery_confidence = min(0.95, trend_confidence * 0.55 + (gap_count * 0.20) + (solution_count * 0.28))
        breakthrough_confidence = min(0.95, discovery_confidence * 0.55 + self._best_solution_score(solutions) * 0.40)

        route_decision = "continue_scan"
        if status in {"blocked", "failed"}:
            route_decision = status
        elif breakthrough_confidence >= self.min_breakthrough_confidence:
            route_decision = "breakthrough_reached"
        elif discovery_confidence >= self.min_discovery_confidence and solution_count:
            route_decision = "discovery_reached"
        elif trend_confidence >= self.min_trend_confidence and signal_base >= self.min_signals_for_trend:
            route_decision = "portfolio_action"

        return {
            "iteration": index,
            "status": status or "unknown",
            "signals_found": signals_found,
            "connector_records": connector_records,
            "governed_signal_count": signal_base,
            "trend_clusters": cluster_count,
            "gaps": gap_count,
            "solutions": solution_count,
            "activated_candidates": activated_count,
            "trend_confidence": round(trend_confidence, 4),
            "discovery_confidence": round(discovery_confidence, 4),
            "breakthrough_confidence": round(breakthrough_confidence, 4),
            "route_decision": route_decision,
            "terminal_reason": self._reason(route_decision, signal_base, solution_count),
        }

    def _terminal(self, progress: Dict[str, Any], index: int) -> Dict[str, Any]:
        decision = progress.get("route_decision")
        if decision in {"blocked", "failed"}:
            return {
                "terminal": True,
                "terminal_state": decision,
                "terminal_reason": progress.get("terminal_reason"),
                "route_selected": f"{decision}_output",
            }
        if decision == "breakthrough_reached":
            return {
                "terminal": True,
                "terminal_state": "breakthrough_reached",
                "terminal_reason": progress.get("terminal_reason"),
                "route_selected": "breakthrough_escalation",
            }
        if decision == "discovery_reached":
            return {
                "terminal": True,
                "terminal_state": "discovery_reached",
                "terminal_reason": progress.get("terminal_reason"),
                "route_selected": "portfolio_creation_optimization",
            }
        if decision == "portfolio_action":
            return {
                "terminal": True,
                "terminal_state": "portfolio_action",
                "terminal_reason": progress.get("terminal_reason"),
                "route_selected": "portfolio_creation_optimization",
            }
        if index >= self.max_iterations:
            if progress.get("governed_signal_count", 0) < self.min_signals_for_trend:
                return {
                    "terminal": True,
                    "terminal_state": "insufficient_data",
                    "terminal_reason": "Scan exhausted enrichment attempts without enough governed signals for trend discovery.",
                    "route_selected": "insufficient_data_output",
                }
            return {
                "terminal": True,
                "terminal_state": "max_iterations_reached",
                "terminal_reason": "Scan reached the max iteration guard before a stronger route threshold was met.",
                "route_selected": "trend_thesis",
            }
        return {"terminal": False}

    def _enrichment_context(self, iterations: List[Dict[str, Any]], result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "last_iteration": iterations[-1] if iterations else {},
            "last_status": result.get("status"),
            "needed": "additional source coverage, signal diversity, or fresh evidence",
        }

    def _reason(self, decision: str, signal_base: int, solution_count: int) -> str:
        if decision == "breakthrough_reached":
            return "Breakthrough confidence met threshold; classify type and select advancement path."
        if decision == "discovery_reached":
            return "Discovery confidence met threshold with solution candidates available."
        if decision == "portfolio_action":
            return "Governed signals support a trend/thesis and portfolio intelligence route."
        if decision == "blocked":
            return "Scan blocked by governance or activation policy."
        if decision == "failed":
            return "Scan runner failed before a route-aware output could be completed."
        if signal_base < self.min_signals_for_trend:
            return "More source signals are needed before trend discovery is credible."
        if not solution_count:
            return "Trend evidence exists, but discovery output is not yet strong enough."
        return "Continue scan enrichment until route threshold or max iteration guard is reached."

    def _best_solution_score(self, solutions: Any) -> float:
        if not isinstance(solutions, list):
            return 0.0
        scores = []
        for solution in solutions:
            if isinstance(solution, dict):
                scores.append(self._float(solution.get("solution_score")))
        return max(scores or [0.0])

    def _get(self, obj: Dict[str, Any], path: str, default: Any = None) -> Any:
        cur: Any = obj if isinstance(obj, dict) else {}
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def _int(self, value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def _float(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0
