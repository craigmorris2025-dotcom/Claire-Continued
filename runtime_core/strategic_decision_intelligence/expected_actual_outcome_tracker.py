from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import InterventionRecommendation, OutcomeRecord


class ExpectedActualOutcomeTracker:
    def create_record(self, recommendation: InterventionRecommendation) -> OutcomeRecord:
        return OutcomeRecord(
            scenario_id=recommendation.scenario_id,
            action_id=recommendation.selected_action_id,
            expected_outcome=recommendation.expected_outcome,
            actual_outcome=None,
            comparison_status="pending_actual",
            variance_notes=["Awaiting later evidence or observed result."],
        )

    def compare(
        self,
        record: OutcomeRecord,
        actual_outcome: Optional[str],
        evidence_updates: Optional[List[Dict[str, Any]]] = None,
    ) -> OutcomeRecord:
        updates = evidence_updates or []
        record.actual_outcome = actual_outcome
        record.evidence_updates.extend(updates)

        if actual_outcome is None:
            record.comparison_status = "pending_actual"
            record.variance_notes.append("No actual outcome supplied.")
            return record

        if actual_outcome == record.expected_outcome:
            record.comparison_status = "matched"
            record.variance_notes.append("Actual outcome matched expected outcome label.")
        elif "uncertain" in record.expected_outcome:
            record.comparison_status = "resolved_from_uncertainty"
            record.variance_notes.append("Actual outcome resolved a previously uncertain expected outcome.")
        else:
            record.comparison_status = "variance_detected"
            record.variance_notes.append("Actual outcome differed from expected outcome label.")

        return record
