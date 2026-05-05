
"""
Acquirer Dataset — loads and provides acquirer profiles.
"""

from typing import List, Dict


class AcquirerDataset:
    """Static + extensible dataset of strategic acquirers."""

    def __init__(self):
        self._data = self._load_default()

    def _load_default(self) -> List[Dict]:
        # You can later replace this with DB/file load
        return [
            {
                "name": "Microsoft",
                "ticker": "MSFT",
                "sector": "technology",
                "focus": ["ai", "cloud", "platform"],
                "capacity": 0.95,
            },
            {
                "name": "Google",
                "ticker": "GOOGL",
                "sector": "technology",
                "focus": ["ai", "data", "search"],
                "capacity": 0.90,
            },
            {
                "name": "Amazon",
                "ticker": "AMZN",
                "sector": "technology",
                "focus": ["cloud", "logistics", "platform"],
                "capacity": 0.92,
            },
            {
                "name": "Lockheed Martin",
                "ticker": "LMT",
                "sector": "defense",
                "focus": ["autonomous", "defense", "aerospace"],
                "capacity": 0.80,
            },
        ]

    def get_all(self) -> List[Dict]:
        return self._data

    def filter_by_sector(self, sector: str) -> List[Dict]:
        return [a for a in self._data if a.get("sector") == sector]
