# Claire Syntalion Enterprise Cockpit

Version marker: v19.66

This folder is the new permanent enterprise cockpit root.

Rules:
- Backend/runtime remains source of truth.
- Cockpit consumes canonical payloads and runtime APIs.
- Old dashboard remains legacy/reference until parity is proven.
- Search is a permanent top-level Claire Command Surface.
- No duplicate fetch ownership.
- No frontend-fabricated runtime truth.

Initial folders:
- shell/
- shared/
- runtime/
- intelligence/
- design/
- package/
- system/
- docs/
