"""
Opportunity Command Catalog — workflow prompts and launch guidance for Claire.

v5.38:
- Defines Claire workflow modes above execution/intelligence modes.
- Preserves execution modes: deterministic, connected intelligence, hybrid.
- Provides command templates for evaluate, discover, expand/optimize, and competitor-beating workflows.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OpportunityCommandCatalog:
    """Deterministic catalog of Claire opportunity commands and search directions."""

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
                "name": "Discover opportunities",
                "description": "Use when the user provides a domain, buyer group, sector, weak signal, or market direction."
            },
            {
                "id": "expand_optimize",
                "name": "Expand / optimize / beat competitors",
                "description": "Use when the user wants stronger wedges, adjacent opportunities, competitor-beating strategy, or upgraded positioning."
            },
        ]

    def sectors(self) -> List[Dict[str, str]]:
        return [
            {"id": "defense_autonomy", "name": "Defense Autonomy"},
            {"id": "climate_insurance", "name": "Climate Insurance"},
            {"id": "healthcare_operations", "name": "Healthcare Operations"},
            {"id": "industrial_supply_chain", "name": "Industrial Supply Chain"},
            {"id": "energy_infrastructure", "name": "Energy Infrastructure"},
            {"id": "financial_intelligence", "name": "Financial Intelligence"},
            {"id": "regulatory_technology", "name": "Regulatory Technology"},
            {"id": "ai_infrastructure", "name": "AI Infrastructure"},
            {"id": "cross_sector", "name": "Cross-Sector"},
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
                "description": "Find the stronger market wedge, stronger buyer pain, stronger moat, and better productization path.",
                "prompt_goal": "improve the project into a more differentiated, defensible, commercially attractive version",
                "default_output_count": 1,
            },
            {
                "id": "discover_non_obvious",
                "workflow": "discover",
                "name": "Discover non-obvious opportunities",
                "description": "Generate opportunity candidates from a domain, buyer group, weak signal, or strategic direction.",
                "prompt_goal": "discover underexploited market gaps and productizable strategic opportunities",
                "default_output_count": 5,
            },
            {
                "id": "discover_regulatory_openings",
                "workflow": "discover",
                "name": "Find regulatory openings",
                "description": "Look for compliance pressure, policy shifts, reporting burdens, or regulated workflow pain that can become a product wedge.",
                "prompt_goal": "surface product opportunities created by regulatory pressure and compliance friction",
                "default_output_count": 5,
            },
            {
                "id": "discover_acquirer_gaps",
                "workflow": "discover",
                "name": "Find acquirer capability gaps",
                "description": "Generate opportunities likely to interest strategic acquirers due to capability gaps or portfolio pressure.",
                "prompt_goal": "identify acquisition-attractive opportunities with clear strategic buyer logic",
                "default_output_count": 5,
            },
            {
                "id": "expand_adjacent",
                "workflow": "expand_optimize",
                "name": "Generate adjacent opportunities",
                "description": "Create adjacent versions of a prior idea or run across buyers, sectors, or product packaging.",
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
            {
                "id": "find_stronger_wedge",
                "workflow": "expand_optimize",
                "name": "Find the stronger wedge",
                "description": "Identify a sharper initial buyer pain, deployment beachhead, or wedge product.",
                "prompt_goal": "convert a broad opportunity into a narrow, high-conviction beachhead wedge",
                "default_output_count": 3,
            },
        ]

    def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        for command in self.commands():
            if command["id"] == command_id:
                return command
        return None

    def catalog(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "execution_modes": self.execution_modes(),
            "workflow_modes": self.workflow_modes(),
            "sectors": self.sectors(),
            "commands": self.commands(),
        }
