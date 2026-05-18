# Claire v19.84.4 Canonical Route Owner Registry

- Generated: `2026-05-13T11:22:15.571711+00:00`
- Status: `configured`
- Validation: `ok`
- Backend owns truth: `True`
- Cockpit owns presentation only: `True`

## Critical Route Owners

| Route | Canonical Owner | Cockpit Role | Audit State | Action |
|---|---|---|---|---|
| `/dashboard/payload` | `backend.enterprise_cockpit_payload_bridge` | `presentation_only` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |
| `/dashboard/payload/status` | `backend.enterprise_cockpit_payload_status` | `presentation_only` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |
| `/runtime/continuous/status` | `backend.continuous_intelligence_runtime_status` | `presentation_only` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |
| `/runtime/continuous/review-queue` | `backend.continuous_intelligence_review_queue` | `presentation_only` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |
| `/runs/start` | `backend.enterprise_runtime_runs_backend` | `operator_command` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |
| `/universes` | `backend.source_universe_backend` | `presentation_only` | `duplicate_owner` | `assign_canonical_and_demote_duplicates` |

## Validation

### Warnings
- /dashboard/payload requires follow-up action: duplicate_owner
- /dashboard/payload/status requires follow-up action: duplicate_owner
- /runtime/continuous/status requires follow-up action: duplicate_owner
- /runtime/continuous/review-queue requires follow-up action: duplicate_owner
- /runs/start requires follow-up action: duplicate_owner
- /universes requires follow-up action: duplicate_owner

## Next Build

v19.84.5 should add the duplicate route fail test and begin enforcing this registry.
