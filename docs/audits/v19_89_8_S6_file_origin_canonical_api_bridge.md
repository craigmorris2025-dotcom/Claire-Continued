# Claire Syntalion v19.89.8-S6 File-Origin Canonical API Bridge

This build fixes visible dashboard panels that fail because the dashboard shell is opened from `file:///`.

The dashboard remains visible through:

`frontend/cockpit/shell/cockpit_shell.html`

Approved backend fetches are rewritten to:

`http://127.0.0.1:8000`

Runtime authority remains blocked.

Console checks:

```js
window.ClaireFileOriginCanonicalApiBridge
window.ClaireFileOriginCanonicalApiBridgeTools.probe()
window.ClaireCanonicalSurfaceWiringTools.run()
window.ClaireSurfaceAvailabilityReconciliationTools.run()
```
