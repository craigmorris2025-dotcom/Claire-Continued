"""Signal clustering and trend formation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


class TrendClusterer:
    """Group extracted signals into trend clusters."""

    def cluster(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for signal in extracted.get("signals", []):
            key = "|".join([
                signal.get("market_universe", "unknown"),
                signal.get("industry_domain", "unknown"),
                signal.get("signal_type", "unknown"),
            ])
            buckets.setdefault(key, []).append(signal)

        clusters = []
        for index, (key, signals) in enumerate(buckets.items(), start=1):
            market_universe, industry_domain, signal_type = key.split("|")
            high_urgency = sum(1 for signal in signals if signal.get("urgency") == "high")
            strength = min(0.95, 0.45 + len(signals) * 0.08 + high_urgency * 0.05)
            clusters.append({
                "cluster_id": f"trend_{index:03d}",
                "market_universe": market_universe,
                "industry_domain": industry_domain,
                "trend_type": signal_type,
                "signal_count": len(signals),
                "entity_count": len({signal.get("entity_id") for signal in signals}),
                "strength_score": round(strength, 3),
                "trajectory": "accelerating" if high_urgency >= 2 else "forming",
                "signals": signals,
                "title": f"{signal_type.replace('_', ' ').title()} trend in {industry_domain.replace('_', ' ')}",
            })

        return {
            "status": "success",
            "clusterer": "trend_clusterer_v1",
            "cluster_count": len(clusters),
            "clusters": sorted(clusters, key=lambda item: item["strength_score"], reverse=True),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
