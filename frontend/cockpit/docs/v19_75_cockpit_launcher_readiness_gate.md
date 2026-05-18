# Claire Syntalion v19.75

## Cockpit Launcher Readiness Gate

This build creates the launcher-readiness gate.

It does not rewire the launcher yet.

## Current intended future launcher target

```text
frontend/cockpit/shell/cockpit_shell.html
```

## Required manual checks before actual launcher rewire

Start Claire, then verify:

```text
http://localhost:8000/dashboard/payload/status
http://localhost:8000/dashboard/payload
```

Then open the cockpit shell directly and confirm the Runtime Payload Gate shows a truthful state.

## Do not delete yet

```text
frontend/command_center/modern/
```

That folder remains legacy reference/fallback until the cockpit is the active launcher target and passes runtime rendering.
