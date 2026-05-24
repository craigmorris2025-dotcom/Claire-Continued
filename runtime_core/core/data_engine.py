"""
DataEngine — provides acquirer profiles for matching.
"""

from typing import List, Dict


class DataEngine:

    def load_acquirers(self) -> List[Dict]:
        return [
            {
                "name": "Lockheed Martin",
                "ticker": "LMT",
                "sector": "defense",
                "fit": 0.92,
                "capacity": 0.88,
                "strategy_alignment": 0.91,
                "tech_alignment": 0.89,
                "focus": ["autonomous systems", "ai", "defense", "drones"],
            },
            {
                "name": "Northrop Grumman",
                "ticker": "NOC",
                "sector": "defense",
                "fit": 0.90,
                "capacity": 0.85,
                "strategy_alignment": 0.88,
                "tech_alignment": 0.90,
                "focus": ["sensor fusion", "autonomous", "drone", "c4isr"],
            },
            {
                "name": "Raytheon",
                "ticker": "RTX",
                "sector": "defense",
                "fit": 0.87,
                "capacity": 0.82,
                "strategy_alignment": 0.86,
                "tech_alignment": 0.88,
                "focus": ["missile systems", "radar", "defense ai"],
            }
        ]

    def query(self, sector: str = None) -> List[Dict]:
        data = self.load_acquirers()
        if sector:
            return [d for d in data if d.get("sector") == sector]
        return data
