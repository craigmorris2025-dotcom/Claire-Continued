"""
Patent Data Connector — patent landscape intelligence.
API-ready: override _live_fetch() for USPTO, Google Patents, Espacenet.
"""
import logging
from typing import Any, Dict, List
from backend.connectors.base import BaseConnector

logger = logging.getLogger("claire.connectors.patent")

PATENT_DATA = {
    "defense": {
        "total_patents": 34000, "pending_applications": 4200,
        "avg_grant_time_months": 28, "patent_density": 0.61, "litigation_rate": 0.02,
        "top_categories": ["Radar/Sensor Systems", "Encryption/COMSEC", "UAV/Autonomous",
                          "Electronic Warfare", "Directed Energy"],
        "key_holders": [
            {"entity": "Raytheon", "patent_count": 4800, "trend": "growing"},
            {"entity": "Lockheed Martin", "patent_count": 4200, "trend": "stable"},
            {"entity": "Northrop Grumman", "patent_count": 3600, "trend": "growing"},
            {"entity": "BAE Systems", "patent_count": 2100, "trend": "stable"},
        ],
        "emerging_areas": ["Quantum sensing", "AI-enabled targeting", "Mesh networking",
                          "Hypersonic guidance", "Space domain awareness"],
        "freedom_to_operate": 0.72,
        "patent_cliff_risk": 0.15,
    },
    "technology": {
        "total_patents": 245000, "pending_applications": 18500,
        "avg_grant_time_months": 22, "patent_density": 0.82, "litigation_rate": 0.04,
        "top_categories": ["Machine Learning", "Natural Language Processing",
                          "Computer Vision", "Cloud Architecture", "Edge Computing"],
        "key_holders": [
            {"entity": "IBM", "patent_count": 42000, "trend": "declining"},
            {"entity": "Samsung", "patent_count": 38000, "trend": "stable"},
            {"entity": "Microsoft", "patent_count": 28000, "trend": "growing"},
            {"entity": "Google", "patent_count": 24000, "trend": "growing"},
        ],
        "emerging_areas": ["Generative AI", "Neuromorphic computing", "Quantum ML",
                          "Federated learning", "Autonomous agents"],
        "freedom_to_operate": 0.58,
        "patent_cliff_risk": 0.08,
    },
    "healthcare": {
        "total_patents": 89000, "pending_applications": 12000,
        "avg_grant_time_months": 26, "patent_density": 0.73, "litigation_rate": 0.06,
        "top_categories": ["Genomics", "Medical Imaging", "Drug Delivery",
                          "Surgical Robotics", "Diagnostic AI"],
        "key_holders": [
            {"entity": "Johnson & Johnson", "patent_count": 12000, "trend": "stable"},
            {"entity": "Medtronic", "patent_count": 9500, "trend": "growing"},
            {"entity": "Abbott", "patent_count": 8200, "trend": "growing"},
        ],
        "emerging_areas": ["mRNA therapeutics", "Digital twins", "AI diagnostics",
                          "Gene editing", "Wearable biosensors"],
        "freedom_to_operate": 0.65,
        "patent_cliff_risk": 0.22,
    },
    "energy": {
        "total_patents": 52000, "pending_applications": 7800,
        "avg_grant_time_months": 24, "patent_density": 0.55, "litigation_rate": 0.03,
        "top_categories": ["Solar PV", "Battery Chemistry", "Grid Management",
                          "Hydrogen Production", "Carbon Capture"],
        "key_holders": [
            {"entity": "Tesla", "patent_count": 3200, "trend": "growing"},
            {"entity": "Siemens", "patent_count": 8500, "trend": "stable"},
            {"entity": "GE", "patent_count": 7800, "trend": "declining"},
        ],
        "emerging_areas": ["Solid-state batteries", "Green hydrogen", "Perovskite solar",
                          "Small modular reactors", "Long-duration storage"],
        "freedom_to_operate": 0.70,
        "patent_cliff_risk": 0.12,
    },
}


class PatentConnector(BaseConnector):
    def get_name(self) -> str:
        return "patent"

    def fetch(self, query: Dict[str, Any], mode: str = "connected") -> Dict[str, Any]:
        return self._safe_fetch(query, mode)

    def _live_fetch(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wire to real patent API here:
          - USPTO PatentsView API (free)
          - Google Patents Public Data (BigQuery)
          - Espacenet Open Patent Services
        Set CLAIRE_PATENT_API_KEY in .env and implement.
        """
        return None

    def fallback(self, query: Dict[str, Any]) -> Dict[str, Any]:
        sector = query.get("sector", query.get("domain", "technology")).lower()
        if sector not in PATENT_DATA:
            sector = "technology"
        data = dict(PATENT_DATA[sector])
        data["sector"] = sector

        # Compute innovation density signal
        keywords = query.get("keywords", [])
        emerging_hits = 0
        for area in data.get("emerging_areas", []):
            for kw in keywords:
                if kw.lower() in area.lower():
                    emerging_hits += 1
        data["emerging_alignment"] = min(1.0, emerging_hits / max(len(data.get("emerging_areas", [1])), 1))
        data["innovation_signal"] = round(
            data["patent_density"] * 0.4 +
            data["emerging_alignment"] * 0.35 +
            (1.0 - data["patent_cliff_risk"]) * 0.25, 4
        )

        logger.info(f"Patent fallback: sector={sector}, innovation_signal={data['innovation_signal']:.3f}")
        return {"connector": "patent", "sector": sector, "data": data}
