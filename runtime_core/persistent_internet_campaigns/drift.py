from __future__ import annotations

from typing import Dict, List


class EvidenceDriftDetector:
    def compare(self, previous_evidence: List[Dict[str, object]], new_evidence: List[Dict[str, object]]) -> Dict[str, object]:
        previous_ids = {str(item.get("evidence_id")) for item in previous_evidence if item.get("evidence_id")}
        new_ids = {str(item.get("evidence_id")) for item in new_evidence if item.get("evidence_id")}

        previous_sources = {str(item.get("source_url")) for item in previous_evidence if item.get("source_url")}
        new_sources_set = {str(item.get("source_url")) for item in new_evidence if item.get("source_url")}

        previous_conf = self.average_confidence(previous_evidence)
        new_conf = self.average_confidence(new_evidence)
        delta = round(new_conf - previous_conf, 4)

        added_sources = sorted(new_sources_set - previous_sources)
        repeated_sources = sorted(new_sources_set & previous_sources)
        removed_sources = sorted(previous_sources - new_sources_set)

        if abs(delta) >= 0.15:
            drift_status = "confidence_shift"
        elif added_sources or removed_sources:
            drift_status = "source_change"
        elif new_ids - previous_ids:
            drift_status = "new_evidence"
        else:
            drift_status = "stable"

        return {
            "previous_average_confidence": previous_conf,
            "new_average_confidence": new_conf,
            "confidence_delta": delta,
            "new_sources": added_sources,
            "repeated_sources": repeated_sources,
            "removed_sources": removed_sources,
            "drift_status": drift_status,
        }

    def average_confidence(self, evidence: List[Dict[str, object]]) -> float:
        if not evidence:
            return 0.0
        values = []
        for item in evidence:
            try:
                values.append(float(item.get("confidence", 0.0)))
            except Exception:
                values.append(0.0)
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)
