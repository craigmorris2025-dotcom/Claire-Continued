# Claire Syntalion v19.70 — Runtime + Lifecycle Panels

## Purpose
Render real runtime data into the new cockpit from the canonical dashboard payload.

## Scope
Created cockpit runtime modules:

- `frontend/cockpit/runtime/runtime_status_panel.js`
- `frontend/cockpit/runtime/lifecycle_panel.js`
- `frontend/cockpit/runtime/run_history_panel.js`
- `frontend/cockpit/runtime/runtime_truth_panel.js`
- `frontend/cockpit/runtime/runtime_workspace.js`
- `frontend/cockpit/runtime/runtime_panel.css`

## Hard Rules Preserved

- Backend owns truth.
- Frontend does not fabricate lifecycle states.
- Frontend does not fabricate run history.
- Frontend does not fabricate evidence.
- Runtime panels consume shared payload adapter context.
- No backend rewrites.
- No launcher rewires.
- No governed web bypass.

## Expected Next Build
v19.71 should wire the runtime workspace into the cockpit shell/registry only after confirming the shell manager contract names from the actual project files.
