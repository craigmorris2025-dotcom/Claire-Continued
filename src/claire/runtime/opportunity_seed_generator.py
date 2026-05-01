"""
Opportunity Seed Generator — deterministic opportunity candidate generator for Claire.

v5.39:
- Converts market universe, industry/domain, buyer segment, objective, and command selections into Claire-ready prompts.
- This does not perform external search; it creates high-quality launch inputs for Claire's pipeline.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.runtime.command_catalog import OpportunityCommandCatalog
from claire.runtime.search_suggestions import OpportunitySearchSuggestions


class OpportunitySeedGenerator:
    """Generate Claire-ready opportunity descriptions from launcher selections."""

    def __init__(self) -> None:
        self.catalog = OpportunityCommandCatalog()
        self.search = OpportunitySearchSuggestions()

    def generate(
        self,
        workflow: str = "discover",
        execution_mode: str = "deterministic",
        market_universe: str = "custom_universe",
        industry_domain: str = "cross_sector",
        buyer_segment: str = "enterprise_c_suite",
        objective: str = "discover_market_gaps",
        command_id: str = "discover_market_gaps",
        signal: str = "",
        count: int = 5,
    ) -> Dict[str, Any]:
        command = self.catalog.get_command(command_id) or self.catalog.get_command("discover_market_gaps")
        suggestions = self.search.suggest(
            market_universe=market_universe,
            industry_domain=industry_domain,
            buyer_segment=buyer_segment,
            objective=objective,
            workflow=workflow,
            signal=signal,
            count=max(count, 5),
        )["suggestions"]

        candidates: List[Dict[str, Any]] = []
        for index in range(max(1, min(count, 10))):
            suggestion = suggestions[index % len(suggestions)]
            title = self._title(market_universe, industry_domain, command["name"], index)
            raw_input = self._raw_input(
                title=title,
                workflow=workflow,
                execution_mode=execution_mode,
                market_universe=market_universe,
                industry_domain=industry_domain,
                buyer_segment=buyer_segment,
                objective=objective,
                command=command,
                signal=signal,
                suggestion=suggestion,
                index=index,
            )
            candidates.append({
                "id": f"candidate_{index + 1}",
                "title": title,
                "market_universe": market_universe,
                "industry_domain": industry_domain,
                "buyer_segment": buyer_segment,
                "objective": objective,
                "workflow": workflow,
                "execution_mode": execution_mode,
                "command_id": command["id"],
                "rationale": self._rationale(command, market_universe, industry_domain, buyer_segment, suggestion),
                "raw_input": raw_input,
            })

        return {
            "status": "success",
            "workflow": workflow,
            "execution_mode": execution_mode,
            "market_universe": market_universe,
            "industry_domain": industry_domain,
            "buyer_segment": buyer_segment,
            "objective": objective,
            "command": command,
            "signal": signal,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    def _title(self, market_universe: str, industry_domain: str, command_name: str, index: int) -> str:
        universe = market_universe.replace("_", " ").title()
        industry = industry_domain.replace("_", " ").title()
        return f"{universe} / {industry} — {command_name} #{index + 1}"

    def _rationale(self, command: Dict[str, Any], market_universe: str, industry_domain: str, buyer_segment: str, suggestion: Dict[str, str]) -> str:
        return (
            f"This candidate is designed to {command.get('prompt_goal')} in the {market_universe.replace('_', ' ')} "
            f"across {industry_domain.replace('_', ' ')} for {buyer_segment.replace('_', ' ')}. "
            f"It uses the exploration seed: {suggestion.get('query')}."
        )

    def _raw_input(
        self,
        title: str,
        workflow: str,
        execution_mode: str,
        market_universe: str,
        industry_domain: str,
        buyer_segment: str,
        objective: str,
        command: Dict[str, Any],
        signal: str,
        suggestion: Dict[str, str],
        index: int,
    ) -> str:
        universe_label = market_universe.replace("_", " ")
        industry_label = industry_domain.replace("_", " ")
        buyer_label = buyer_segment.replace("_", " ")
        objective_label = objective.replace("_", " ")
        signal_text = signal.strip() or suggestion.get("query", "")

        if workflow == "evaluate":
            opening = (
                f"Evaluate and optimize the following strategic opportunity for the {universe_label} market universe, "
                f"focused on {industry_label} and {buyer_label}: {signal_text}. "
                f"Improve the concept into a more defensible, productizable, acquisition-attractive opportunity."
            )
        elif workflow == "expand_optimize":
            opening = (
                f"Expand, optimize, and reframe this opportunity so it can beat direct competitors in the {universe_label} universe, "
                f"within {industry_label}, for {buyer_label}: {signal_text}. "
                f"Find a stronger wedge, sharper buyer pain, stronger moat, better proof path, and more compelling strategic positioning."
            )
        else:
            opening = (
                f"Discover a non-obvious strategic opportunity in the {universe_label} market universe, within {industry_label}, "
                f"for {buyer_label}, with the objective to {objective_label}: {signal_text}. "
                f"Generate a productizable market gap with clear buyer pain, urgency, adoption path, defensibility, and acquisition logic."
            )

        return (
            f"{opening} "
            f"Workflow mode: {workflow}. Execution mode requested: {execution_mode}. "
            f"Command: {command.get('name')} — {command.get('description')} "
            f"The result should identify the target buyer, painful workflow, missing solution, technical feasibility path, regulatory or governance constraints, "
            f"competitive alternatives, what would beat direct competitors, initial wedge product, pilot path, productization path, strategic positioning, "
            f"deal/acquirer logic, market-universe coverage logic, and export-ready portfolio thesis. Candidate variant: {index + 1}."
        )
