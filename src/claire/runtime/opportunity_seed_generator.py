"""
Opportunity Seed Generator — deterministic opportunity candidate generator for Claire.

v5.38:
- Converts command selections, sectors, and signals into Claire-ready raw_input prompts.
- This does not perform external search; it creates high-quality launch inputs for Claire's pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.runtime.command_catalog import OpportunityCommandCatalog
from claire.runtime.search_suggestions import OpportunitySearchSuggestions


class OpportunitySeedGenerator:
    """Generate Claire-ready opportunity descriptions from command and sector selections."""

    def __init__(self) -> None:
        self.catalog = OpportunityCommandCatalog()
        self.search = OpportunitySearchSuggestions()

    def generate(
        self,
        workflow: str = "discover",
        execution_mode: str = "deterministic",
        sector: str = "cross_sector",
        command_id: str = "discover_non_obvious",
        signal: str = "",
        count: int = 5,
    ) -> Dict[str, Any]:
        command = self.catalog.get_command(command_id) or self.catalog.get_command("discover_non_obvious")
        suggestions = self.search.suggest(sector=sector, workflow=workflow, signal=signal, count=max(count, 5))["suggestions"]

        candidates: List[Dict[str, Any]] = []
        for index in range(max(1, min(count, 10))):
            suggestion = suggestions[index % len(suggestions)]
            title = self._title(sector, command["name"], index)
            raw_input = self._raw_input(
                title=title,
                workflow=workflow,
                execution_mode=execution_mode,
                sector=sector,
                command=command,
                signal=signal,
                suggestion=suggestion,
                index=index,
            )
            candidates.append({
                "id": f"candidate_{index + 1}",
                "title": title,
                "sector": sector,
                "workflow": workflow,
                "execution_mode": execution_mode,
                "command_id": command["id"],
                "rationale": self._rationale(command, sector, suggestion),
                "raw_input": raw_input,
            })

        return {
            "status": "success",
            "workflow": workflow,
            "execution_mode": execution_mode,
            "sector": sector,
            "command": command,
            "signal": signal,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    def _title(self, sector: str, command_name: str, index: int) -> str:
        sector_label = sector.replace("_", " ").title()
        return f"{sector_label} — {command_name} #{index + 1}"

    def _rationale(self, command: Dict[str, Any], sector: str, suggestion: Dict[str, str]) -> str:
        return (
            f"This candidate is designed to {command.get('prompt_goal')} in {sector.replace('_', ' ')}. "
            f"It uses the exploration seed: {suggestion.get('query')}."
        )

    def _raw_input(
        self,
        title: str,
        workflow: str,
        execution_mode: str,
        sector: str,
        command: Dict[str, Any],
        signal: str,
        suggestion: Dict[str, str],
        index: int,
    ) -> str:
        sector_label = sector.replace("_", " ")
        signal_text = signal.strip() or suggestion.get("query", "")

        if workflow == "evaluate":
            opening = (
                f"Evaluate and optimize the following strategic opportunity in {sector_label}: {signal_text}. "
                f"Improve the concept into a more defensible, productizable, acquisition-attractive opportunity."
            )
        elif workflow == "expand_optimize":
            opening = (
                f"Expand, optimize, and reframe this opportunity so it can beat direct competitors in {sector_label}: {signal_text}. "
                f"Find a stronger wedge, sharper buyer pain, stronger moat, better proof path, and more compelling strategic positioning."
            )
        else:
            opening = (
                f"Discover a non-obvious strategic opportunity in {sector_label} using this signal: {signal_text}. "
                f"Generate a productizable market gap with clear buyer pain, urgency, adoption path, defensibility, and acquisition logic."
            )

        return (
            f"{opening} "
            f"Workflow mode: {workflow}. Execution mode requested: {execution_mode}. "
            f"Command: {command.get('name')} — {command.get('description')} "
            f"The result should identify the target buyer, painful workflow, missing solution, technical feasibility path, regulatory or governance constraints, "
            f"competitive alternatives, what would beat direct competitors, initial wedge product, pilot path, productization path, strategic positioning, "
            f"deal/acquirer logic, and export-ready portfolio thesis. Candidate variant: {index + 1}."
        )
