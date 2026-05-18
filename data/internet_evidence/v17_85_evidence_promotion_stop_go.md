# Claire v17.85 Governed Web Evidence Promotion Gate

Generated: 2026-05-13T11:20:33.085039Z

Status: **PROMOTION_REVIEW_READY_WITH_WARNINGS**

Recommendation: Review evidence candidates. Do not promote quarantined or unreviewed records. Runtime truth ingestion remains disabled.

## Hard Rules

- This build does not promote evidence automatically.
- Promotion requires manual review and confirm text.
- Promotion writes to reviewed web evidence store only.
- Runtime truth ingestion remains disabled.
- Quarantined records remain in quarantine review.
- Automatic updates and agent execution remain disabled.

## Files

- `data\internet_evidence\promoted_evidence_candidates_template.json`
- `data\internet_evidence\quarantine_review_queue.json`
- `data\internet_evidence\promoted_evidence_store.json`

## Required confirm text

`PROMOTE REVIEWED EVIDENCE`

## Counts

- Evidence candidates: 0
- Quarantine records: 0

## Warnings

- last_live_probe_not_executed_or_missing
- no_promotion_candidates_created

## Swagger promotion endpoint

POST `/internet/evidence-promotion/promote-approved`

```json
{
  "confirm_text": "PROMOTE REVIEWED EVIDENCE"
}
```
