from __future__ import annotations

from typing import Dict, List


class CrossCampaignMemoryFusion:
    def fuse(self, campaigns: List[Dict[str, object]]) -> Dict[str, object]:
        topic_counts: Dict[str, int] = {}
        total_confidence = 0.0

        for campaign in campaigns:
            total_confidence += float(campaign.get("confidence", 0.0))
            for topic in campaign.get("topics", []):
                topic_counts[str(topic)] = topic_counts.get(str(topic), 0) + 1

        repeated_topics = [topic for topic, count in topic_counts.items() if count > 1]
        avg_confidence = total_confidence / len(campaigns) if campaigns else 0.0

        return {
            "campaign_count": len(campaigns),
            "topic_counts": topic_counts,
            "repeated_topics": repeated_topics,
            "average_confidence": round(avg_confidence, 4),
            "fusion_status": "ready" if campaigns else "empty",
        }
