# Claire Syntalion v19.73

## Cockpit Runtime Payload Gate Wiring

This build adds the actual cockpit-side bridge module:

```text
frontend/cockpit/runtime/runtime_payload_gate.js
```

It wires together:

```text
frontend/cockpit/shared/payload_route_guard.js
frontend/cockpit/runtime/runtime_render_gate.js
frontend/cockpit/shared/api_client.js
frontend/cockpit/shared/payload_adapter.js
```

## Runtime rule

The cockpit may only render runtime state when canonical backend payload routes are available.

If `/dashboard/payload/status` or `/dashboard/payload` is unavailable, the runtime workspace must remain blocked/truthfully unavailable.

## Not changed

```text
LAUNCH_CLAIRE.bat
frontend/command_center/modern/index.html
claire/app.py
```

## Next build

v19.74 should connect this bridge to the visible cockpit shell/workspace manager once pytest passes.
