"""
Opportunity Command Catalog — workflow prompts and launch guidance for Claire.

v5.39:
- Uses industry-standard launcher terminology.
- Separates market universe, industry/domain, buyer segment, and objective.
- Preserves execution modes: deterministic, connected intelligence, hybrid.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from claire.runtime.market_universe_taxonomy import MarketUniverseTaxonomy


class OpportunityCommandCatalog:
    """Deterministic catalog of Claire opportunity commands and market-universe controls."""

    def __init__(self) -> None:
        self.taxonomy = MarketUniverseTaxonomy()

    def execution_modes(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "deterministic",
                "name": "Deterministic",
                "description": "Sealed, reproducible, patent-safe first-principles evaluation with no external data."
            },
            {
                "id": "connected",
                "name": "Connected Intelligence",
                "description": "Live/connected strategic intelligence mode for market, competitor, regulatory, and acquisition signals."
            },
            {
                "id": "hybrid",
                "name": "Hybrid",
                "description": "Dual-core mode combining deterministic logic and connected intelligence under governance."
            },
        ]

    def workflow_modes(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "evaluate",
                "name": "Evaluate described opportunity",
                "description": "Use when the user already has a project, product, thesis, or strategic opportunity."
            },
            {
                "id": "discover",
                "name": "Discover opportunities from market universe",
                "description": "Use when the user provides a market universe, industry/domain, buyer group, or weak signal."
            },
            {
                "id": "expand_optimize",
                "name": "Expand / optimize / beat competitors",
                "description": "Use when the user wants stronger wedges, adjacent opportunities, competitor-beating strategy, or upgraded positioning."
            },
        ]

    def commands(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "evaluate_project",
                "workflow": "evaluate",
                "name": "Evaluate and package this project",
                "description": "Score, expand, productize, position, and export a user-described project.",
                "prompt_goal": "turn a described project into an export-ready strategic opportunity package",
                "default_output_count": 1,
            },
            {
                "id": "optimize_project",
                "workflow": "evaluate",
                "name": "Optimize this project into a stronger opportunity",
                "description": "Find the stronger market wedge, buyer pain, moat, proof path, and productization strategy.",
                "prompt_goal": "improve the project into a more differentiated, defensible, commercially attractive version",
                "default_output_count": 1,
            },
            {
                "id": "discover_market_gaps",
                "workflow": "discover",
                "name": "Discover market gaps",
                "description": "Generate opportunity candidates from a market universe, industry/domain, buyer segment, and weak signal.",
                "prompt_goal": "discover underexploited market gaps and productizable strategic opportunities",
                "default_output_count": 5,
            },
            {
                "id": "find_acquirer_gaps",
                "workflow": "discover",
                "name": "Find acquirer capability gaps",
                "description": "Generate opportunities likely to interest strategic acquirers due to capability gaps or portfolio pressure.",
                "prompt_goal": "identify acquisition-attractive opportunities with clear strategic buyer logic",
                "default_output_count": 5,
            },
            {
                "id": "find_regulatory_openings",
                "workflow": "discover",
                "name": "Find regulatory openings",
                "description": "Look for compliance pressure, policy shifts, reporting burdens, or regulated workflow pain that can become a product wedge.",
                "prompt_goal": "surface product opportunities created by regulatory pressure and compliance friction",
                "default_output_count": 5,
            },
            {
                "id": "find_workflow_bottlenecks",
                "workflow": "discover",
                "name": "Find workflow bottlenecks",
                "description": "Find expensive, repeated, measurable operational bottlenecks that can be converted into software, intelligence, or automation products.",
                "prompt_goal": "identify urgent workflow bottlenecks with budget, ownership, and measurable ROI",
                "default_output_count": 5,
            },
            {
                "id": "generate_adjacent_opportunities",
                "workflow": "expand_optimize",
                "name": "Generate adjacent opportunities",
                "description": "Create adjacent versions of a prior idea or run across buyers, industries, or product packaging.",
                "prompt_goal": "expand one thesis into multiple adjacent opportunity candidates",
                "default_output_count": 5,
            },
            {
                "id": "beat_competitors",
                "workflow": "expand_optimize",
                "name": "Reframe to beat direct competitors",
                "description": "Find the positioning, product, moat, buyer, and proof path that would outcompete direct alternatives.",
                "prompt_goal": "reframe the opportunity into a competitor-beating strategy",
                "default_output_count": 3,
            },
        ]

    def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        for command in self.commands():
            if command["id"] == command_id:
                return command
        return None

    def catalog(self) -> Dict[str, Any]:
        taxonomy = self.taxonomy.catalog()
        return {
            "status": "success",
            "execution_modes": self.execution_modes(),
            "workflow_modes": self.workflow_modes(),
            "commands": self.commands(),
            "market_universes": taxonomy["market_universes"],
            "industry_domains": taxonomy["industry_domains"],
            "buyer_segments": taxonomy["buyer_segments"],
            "opportunity_objectives": taxonomy["opportunity_objectives"],
            "internal_routing_hints": taxonomy["internal_routing_hints"],
        }
