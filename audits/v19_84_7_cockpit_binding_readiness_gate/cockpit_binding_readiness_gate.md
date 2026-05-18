# Claire v19.84.7 Cockpit Binding Readiness Gate

- Generated: `2026-05-13T11:22:15.668710+00:00`
- Status: `blocked`
- Ready for cockpit binding: `False`
- Backend owns truth: `True`
- Cockpit owns presentation only: `True`
- Allowed next build: `v19.84.8 Critical Route Resolution`

## Blockers

- `route_authority` — `critical_route_failures_present`
  - Required action: Resolve v19.84.5 critical duplicate/missing route failures before cockpit binding.
- `consolidation` — `v19_84_6_consolidation_required`
  - Required action: Do not proceed to cockpit binding lock until critical route failures are resolved.

## Warnings

No warnings.
