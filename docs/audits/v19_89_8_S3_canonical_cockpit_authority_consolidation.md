# Claire Syntalion v19.89.8-S3 Canonical Cockpit Authority Consolidation

This build selects the active cockpit authority chain by manifest only.

## Active shell

`frontend/cockpit/shell/cockpit_shell.html`

## Runtime authority

`safe_to_expand_runtime_authority = false`

## Rule

Patch only the canonical active chain. Do not patch old command center, export dashboard, unified dashboard, or beacon files unless restoring/archiving later.

## Canonical routes

- `/dashboard/payload`
- `/dashboard/payload/status`
- `/system/cockpit-fetch-map/summary`
- `/system/route-owner-registry/summary`
- `/system/duplicate-route-fail-test/summary`
- `/system/runtime-execution/summary`
- `/system/runtime-state/summary`
- `/system/runtime-propagation/summary`
- `/system/review-queue/summary`