# Claire Syntalion v19.72

## Cockpit Payload Route Gate + Runtime Render Verification

This pack is intentionally non-destructive.

It confirms the current migration reality:

- backend remains the source of truth
- cockpit must consume canonical payload only
- legacy dashboard is not deleted
- launcher is not rewired yet
- no frontend fallback may fabricate runtime truth

## Canonical backend payload routes

```text
/dashboard/payload/status
/dashboard/payload
```

## Added files

```text
frontend/cockpit/shared/payload_route_guard.js
frontend/cockpit/runtime/runtime_render_gate.js
tests/test_v19_72_cockpit_payload_route_gate.py
audits/v19_72_cockpit_payload_route_gate/
```

## Required next manual checks

Start Claire, then check:

```text
http://localhost:8000/dashboard/payload/status
http://localhost:8000/dashboard/payload
```

If both return valid data, cockpit payload bridge can be treated as unblocked.

If either fails, do not rewire launcher yet.
