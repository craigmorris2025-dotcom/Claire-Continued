# Claire v17.50 — Dashboard Runtime Alignment + Action Buttons

This build bridges the installed backend capability stack to the dashboard.

## What it adds

- Governed dashboard action button registry
- Dashboard alignment FastAPI routes
- Dashboard capability manifest generation
- Frontend action panel script
- Safe HTML script injection into detected dashboard HTML files
- Regression tests for route contracts, button contracts, and manifest generation

## Governance constraints

- Buttons call declared HTTP routes only.
- Buttons do not execute shell commands.
- Button registry allows only bounded GET/POST actions.
- Backend route inclusion is patch-backed with rollback copies.
- Runtime feature state is exposed through manifests and inspection endpoints.

## First-use checks

1. Start the backend.
2. Open the dashboard or `/docs`.
3. Verify `/dashboard/alignment/status` returns `status`.
4. Verify `/dashboard/alignment/buttons` returns the button list.
5. Open the dashboard and use the v17.50 floating action panel.
6. Any failed route result indicates a dashboard/backend mismatch to fix next.
