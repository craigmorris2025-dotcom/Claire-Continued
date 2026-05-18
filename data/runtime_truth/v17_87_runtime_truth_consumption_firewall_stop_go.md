# Claire Syntalion v17.87 — Runtime Truth Consumption Firewall

## Status

READY FOR TESTING

## Purpose

v17.87 creates a read-only firewall between the runtime truth ledger and any Claire runtime/dashboard/search-bar consumer.

This prevents evidence from being treated as usable runtime truth unless it has passed the v17.86 reviewed-ingestion contract.

## Hard Rules

- Runtime truth must be consumed through the firewall.
- Runtime truth records are read-only.
- Automatic updates remain disabled.
- Autonomous agent execution remains disabled.
- Runtime truth mutation remains disabled.
- Direct live web probe output remains blocked.
- Missing-lineage evidence remains blocked.
- Duplicate evidence IDs remain blocked.
- Unapproved or incorrectly promoted evidence remains blocked.

## Eligible Runtime Truth Requirements

A record is eligible only when:

1. runtime_truth_id exists
2. evidence_id exists
3. ingestion_mode == manual_reviewed_append_only
4. source_provenance exists
5. approved_by exists
6. approved_at exists
7. lineage exists
8. lineage.live_probe_direct_ingestion == false
9. lineage.automatic_update == false
10. lineage.autonomous_ingestion == false
11. lineage.candidate_review_status == approved
12. lineage.candidate_promotion_status == approved_for_runtime_truth
13. evidence_id is not duplicated in the ledger

## Outputs

- data/runtime_truth/runtime_truth_consumption_report.json

## Stop / Go

GO only if pytest passes and the consumption report blocks unsafe runtime truth while allowing only clean reviewed records.
