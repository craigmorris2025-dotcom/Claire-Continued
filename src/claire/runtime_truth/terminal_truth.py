from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping

from .runtime_truth_contract import FAILURE_TERMINALS, FINAL_TERMINALS, ROUTE_TERMINALS, SUCCESS_TERMINALS, first_present, normalize_route, normalize_terminal


@dataclass
class TerminalTruth:
    terminal_state: str
    terminal_type: str
    is_final: bool
    route_fit: bool
    reason: str


def build_terminal_truth(raw: Mapping[str, Any], selected_route: str) -> Dict[str, Any]:
    terminal = normalize_terminal(first_present(raw, ["terminal_state", "status_terminal", "core_lifecycle_summary.terminal_state", "status"], "")) or "not_reported"
    route = normalize_route(selected_route)
    if terminal in SUCCESS_TERMINALS:
        terminal_type = "success"
    elif terminal in FAILURE_TERMINALS:
        terminal_type = "failure"
    elif terminal in {"pending", "running", "in_progress"}:
        terminal_type = "non_terminal"
    else:
        terminal_type = "unknown"
    route_fit = terminal in ROUTE_TERMINALS.get(route, set()) if route else False
    if terminal == "not_reported":
        reason = "No terminal state was reported by runtime output."
    elif not terminal in FINAL_TERMINALS:
        reason = "Terminal state is not one of the canonical final states."
    elif route and not route_fit:
        reason = "Terminal state is final but does not fit the selected route contract."
    else:
        reason = "Terminal state satisfies canonical final-state requirements."
    return asdict(TerminalTruth(terminal, terminal_type, terminal in FINAL_TERMINALS, route_fit, reason))
