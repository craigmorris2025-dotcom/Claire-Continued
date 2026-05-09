"""
Opportunity Seed Generator — protected opportunity candidate generator for Claire.

v5.40:
- Generates safe public opportunity cards plus protected raw Claire launch prompts.
- UI should display only public fields.
- Raw prompts remain server-side through OpportunityCandidateStore.
"""

from __future__ import annotations

from typing import Any, Dict, List

from claire.runtime.command_catalog import OpportunityCommandCatalog
from claire.runtime.search_suggestions import OpportunitySearchSuggestions


class OpportunitySeedGenerator:
    """Generate protected opportunity candidates from launcher selections."""

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
        directions = self.search.suggest(
            market_universe=market_universe,
            industry_domain=industry_domain,
            buyer_segment=buyer_segment,
            objective=objective,
            workflow=workflow,
            signal=signal,
            count=max(count, 5),
        )["directions"]

        candidates: List[Dict[str, Any]] = []
        for index in range(max(1, min(count, 10))):
            direction = directions[index % len(directions)]
            title = self._title(market_universe, industry_domain, objective, index)
            public = {
                "title": title,
                "market_universe": market_universe,
                "industry_domain": industry_domain,
                "buyer_segment": buyer_segment,
                "objective": objective,
                "workflow": workflow,
                "execution_mode": execution_mode,
                "command_id": command["id"],
                "opportunity_direction": direction["opportunity_direction"],
                "market_gap": direction["market_gap"],
                "needed_solution": direction["needed_solution"],
                "why_now": direction["why_now"],
                "selection_score": round(0.82 + (index * 0.02), 2) if index < 5 else 0.84,
                "confidence_label": "high" if index < 3 else "medium",
            }
            raw_input = self._raw_input(public, command, signal, index)
            candidate = dict(public)
            candidate["raw_input"] = raw_input
            candidates.append(candidate)

        return {
            "status": "success",
            "workflow": workflow,
            "execution_mode": execution_mode,
            "market_universe": market_universe,
            "industry_domain": industry_domain,
            "buyer_segment": buyer_segment,
            "objective": objective,
            "command": {
                "id": command["id"],
                "name": command["name"],
                "description": command["description"],
            },
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    def _title(self, market_universe: str, industry_domain: str, objective: str, index: int) -> str:
        universe = market_universe.replace("_", " ").title()
        industry = industry_domain.replace("_", " ").title()
        objective_label = objective.replace("_", " ").title()
        return f"{objective_label} — {industry} / {universe} #{index + 1}"

    def _raw_input(self, public: Dict[str, Any], command: Dict[str, Any], signal: str, index: int) -> str:
        return (
            f"Evaluate this strategic opportunity candidate. "
            f"Market universe: {public['market_universe'].replace('_', ' ')}. "
            f"Industry/domain: {public['industry_domain'].replace('_', ' ')}. "
            f"Buyer segment: {public['buyer_segment'].replace('_', ' ')}. "
            f"Opportunity objective: {public['objective'].replace('_', ' ')}. "
            f"Opportunity direction: {public['opportunity_direction']}. "
            f"Market gap: {public['market_gap']} "
            f"Needed solution: {public['needed_solution']} "
            f"Why now: {public['why_now']} "
            f"User signal: {signal.strip() or 'none provided'}. "
            f"Command: {command.get('name')} — {command.get('description')}. "
            f"Produce an export-ready opportunity package that identifies the target buyer, painful workflow, missing solution, "
            f"technical feasibility path, governance or regulatory constraints, competitive alternatives, what beats direct competitors, "
            f"initial wedge product, pilot path, productization path, strategic positioning, acquirer logic, and portfolio thesis. "
            f"Candidate variant: {index + 1}."
        )
