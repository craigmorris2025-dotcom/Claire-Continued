# Claire v19.84.9 Cockpit Binding Contract Lock

- Generated: `2026-05-13T11:22:15.798711+00:00`
- Status: `locked_with_warnings`
- Backend owns truth: `True`
- Cockpit owns presentation only: `True`
- Allowed fetches: `8`
- Observed fetches: `23`
- Blockers: `0`
- Warnings: `16`

## Allowed Fetch Contract

- `GET /dashboard/payload` — Primary cockpit runtime payload.
- `GET /dashboard/payload/status` — Payload availability and backend truth status.
- `GET /runtime/continuous/status` — Continuous governed runtime status.
- `GET /runtime/continuous/review-queue` — Operator review queue.
- `POST /runs/start` — Operator-commanded manual run start.
- `GET /universes` — Configured source universe list.
- `GET /health` — Backend runtime health check.
- `GET /docs` — Developer/API documentation surface; not an operator cockpit dependency.

## Blockers

No blockers.

## Warnings

- `/>
        <path d=` — `fetch_route_not_in_allowed_contract`
- `/api/command` — `fetch_route_not_in_allowed_contract`
- `/api/commands` — `fetch_route_not_in_allowed_contract`
- `/api/dashboard/search/live` — `fetch_route_not_in_allowed_contract`
- `/api/dashboard/state` — `fetch_route_not_in_allowed_contract`
- `/api/feeds/live-source-catalog/health-check` — `fetch_route_not_in_allowed_contract`
- `/api/feeds/public-company-live/status` — `fetch_route_not_in_allowed_contract`
- `/api/platform/resolve` — `fetch_route_not_in_allowed_contract`
- `/api/platform/status` — `fetch_route_not_in_allowed_contract`
- `/dashboard/alignment/buttons` — `fetch_route_not_in_allowed_contract`
- `/exports/index.json` — `fetch_route_not_in_allowed_contract`
- `/operator/dashboard/state` — `fetch_route_not_in_allowed_contract`
- `/runs/latest` — `fetch_route_not_in_allowed_contract`
- `/runtime/continuous/pause` — `fetch_route_not_in_allowed_contract`
- `/runtime/continuous/start` — `fetch_route_not_in_allowed_contract`
- `/system/cockpit-truth` — `fetch_route_not_in_allowed_contract`

Next build: `v19.85.0 Evidence Escalation Hardening`
