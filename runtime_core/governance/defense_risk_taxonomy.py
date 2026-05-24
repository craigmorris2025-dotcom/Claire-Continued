"""
Defense Risk Taxonomy — lawful pathway classification for Claire.

v5.42:
- Defense work is not automatically treated as autonomous weaponization.
- Classifies opportunity text into allow / review / block tiers.
- Preserves lawful breakthrough and opportunity pathways while logging legal/compliance issues.
"""

from __future__ import annotations

from typing import Any, Dict, List


class DefenseRiskTaxonomy:
    """Tiered defense and redline taxonomy."""

    def tiers(self) -> List[Dict[str, Any]]:
        return [
            {
                "tier": 0,
                "id": "normal_defense_government",
                "name": "Normal defense / government opportunity",
                "decision": "allow",
                "description": "Lawful business, logistics, readiness, compliance, procurement, training, auditability, secure workflow, reporting, supply chain, or human-review support.",
            },
            {
                "tier": 1,
                "id": "dual_use_defense_adjacent",
                "name": "Dual-use / defense-adjacent",
                "decision": "allow_with_log",
                "description": "Sensors, simulation, autonomy support, ISR-adjacent analytics, mission planning support, critical infrastructure defense, or secure communications without autonomous harm enablement.",
            },
            {
                "tier": 2,
                "id": "sensitive_defense_component",
                "name": "Controlled / sensitive defense platform component",
                "decision": "review",
                "description": "Platform components or capabilities that may affect targeting, weapons systems, platform control, operational mission execution, export-controlled defense capability, or classified-adjacent contexts.",
            },
            {
                "tier": 3,
                "id": "autonomous_weaponization",
                "name": "Autonomous weaponization hard stop",
                "decision": "block",
                "description": "Autonomous target selection, autonomous engagement, weapons release, lethality optimization, evasion for weaponized systems, or instructions that materially enable autonomous harm.",
            },
        ]

    def categories(self) -> Dict[str, List[str]]:
        return {
            "normal_defense_government": [
                "logistics", "maintenance", "readiness", "procurement", "compliance",
                "training", "auditability", "audit log", "secure workflow", "reporting",
                "supply chain", "human review", "human authorization", "operator review",
                "mission support", "command review", "risk visibility", "program management",
            ],
            "dual_use_defense_adjacent": [
                "sensor", "simulation", "autonomy support", "isr", "intelligence surveillance reconnaissance",
                "mission planning support", "critical infrastructure", "secure communications",
                "situational awareness", "command center", "decision support", "coordination",
            ],
            "sensitive_defense_component": [
                "targeting", "weapons system", "weapon system", "platform control", "fire control",
                "guidance", "navigation for weapon", "payload", "munitions", "missile",
                "drone swarm", "combat platform", "export controlled", "itar", "ear99",
                "classified", "classified-adjacent", "operational mission execution",
            ],
            "autonomous_weaponization": [
                "autonomous target selection", "autonomous targeting", "autonomous engagement",
                "weapons release", "autonomous weapons release", "lethality optimization",
                "kill chain automation", "automated kill chain", "lethal autonomous",
                "weaponized evasion", "evade defenses", "terminal guidance for weapon",
                "select and engage targets", "identify and kill", "autonomous strike",
            ],
        }

    def hard_stops(self) -> List[str]:
        return [
            "autonomous_weaponization",
            "export_control_violation",
            "classified_adjacent_unapproved",
            "critical_bio_risk",
        ]
