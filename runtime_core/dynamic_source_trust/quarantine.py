from __future__ import annotations

from .models import SourceTrustProfile


class SourceQuarantineEngine:
    def evaluate(self, profile: SourceTrustProfile) -> SourceTrustProfile:
        if profile.correction_events >= 2:
            profile.status = "quarantined"
            if "Quarantined because correction/retraction events reached threshold." not in profile.notes:
                profile.notes.append("Quarantined because correction/retraction events reached threshold.")
            return profile

        if profile.negative_events >= 3:
            profile.status = "quarantined"
            if "Quarantined because negative trust events reached threshold." not in profile.notes:
                profile.notes.append("Quarantined because negative trust events reached threshold.")
            return profile

        if profile.adaptive_score < 0.35 or profile.contradiction_events >= 3:
            profile.status = "degraded"
            if "Degraded because adaptive trust or contradiction count crossed threshold." not in profile.notes:
                profile.notes.append("Degraded because adaptive trust or contradiction count crossed threshold.")
            return profile

        if profile.status in {"degraded", "quarantined"} and profile.adaptive_score >= 0.65 and profile.negative_events == 0:
            profile.status = "active"

        return profile
