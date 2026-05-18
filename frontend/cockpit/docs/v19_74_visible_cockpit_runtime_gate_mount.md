# Claire Syntalion v19.74

## Visible Cockpit Runtime Gate Mount

This build makes the runtime payload gate visible inside the cockpit shell.

## Changed

```text
frontend/cockpit/shell/cockpit_shell.html
frontend/cockpit/shell/cockpit_bootstrap.js
frontend/cockpit/shell/cockpit_shell.css
```

## Uses

```text
frontend/cockpit/runtime/runtime_payload_gate.js
frontend/cockpit/shared/api_client.js
frontend/cockpit/shared/payload_adapter.js
```

## Not changed

```text
LAUNCH_CLAIRE.bat
frontend/command_center/modern/index.html
claire/app.py
```

## Rule

If canonical backend payload routes are unavailable, the visible cockpit gate must show blocked/unavailable, not fake runtime data.
