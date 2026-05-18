# Claire System vs Dashboard Operation Gap Audit

- Version: `v19.89.8-S1295-S1322-system-vs-dashboard-operation-gap-audit`
- Generated: `2026-05-18T19:26:21.722484+00:00`
- Backend routes: **561**
- Frontend fetches found: **1**
- Frontend buttons found: **68**
- Required capabilities: **15**
- Bound required capabilities: **1**
- Lagging required capabilities: **14**
- Dashboard operational binding score: **6.67%**
- Audit status: **dashboard_lagging_backend**

## Capability gap table

| Capability | Backend routes | Fetch bound | Button present | Status |
|---|---:|---|---|---|
| System health, plateau lock, and audit proof | 7 | False | True | `button_without_fetch_binding` |
| Canonical dashboard payload and status | 2 | False | True | `button_without_fetch_binding` |
| Dashboard action registry, summary, preview, and result | 8 | False | True | `button_without_fetch_binding` |
| Operator console controls and action result binding | 10 | True | True | `bound` |
| Cockpit operations, control surface, and visual operations | 31 | False | True | `button_without_fetch_binding` |
| Command bar operation payload, buttons, and preview | 7 | False | True | `button_without_fetch_binding` |
| Governed search planning and search result surfaces | 36 | False | True | `button_without_fetch_binding` |
| Search provider readiness, configuration, manual probe, and stop gates | 27 | False | True | `button_without_fetch_binding` |
| Metadata probe, controlled live probe, and governed web probe boundaries | 34 | False | True | `button_without_fetch_binding` |
| Evidence quarantine, evidence cards, review, and promotion preview | 37 | False | True | `button_without_fetch_binding` |
| Source registry, source policy, gaps, intake, and live source catalog | 34 | False | True | `button_without_fetch_binding` |
| Body-read authorization, extraction scope, sanitizer, manual gate, and stop gate | 41 | False | True | `button_without_fetch_binding` |
| Runtime spine, evidence lifecycle, routing preview, and operator control | 13 | False | True | `button_without_fetch_binding` |
| Update proposal, runtime truth promotion preview, and source ingestion draft | 7 | False | True | `button_without_fetch_binding` |
| Live intelligence status and live source catalog health | 3 | False | True | `button_without_fetch_binding` |

## Lagging required capabilities

- **System health, plateau lock, and audit proof** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Canonical dashboard payload and status** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Dashboard action registry, summary, preview, and result** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Cockpit operations, control surface, and visual operations** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Command bar operation payload, buttons, and preview** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Governed search planning and search result surfaces** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Search provider readiness, configuration, manual probe, and stop gates** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Metadata probe, controlled live probe, and governed web probe boundaries** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Evidence quarantine, evidence cards, review, and promotion preview** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Source registry, source policy, gaps, intake, and live source catalog** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Body-read authorization, extraction scope, sanitizer, manual gate, and stop gate** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Runtime spine, evidence lifecycle, routing preview, and operator control** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Update proposal, runtime truth promotion preview, and source ingestion draft** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.
- **Live intelligence status and live source catalog health** — `button_without_fetch_binding` — Dashboard appears to have a control, but no matching backend fetch/result binding was found.

## Next recommended build

- **S1323-S1350 — Dashboard Operations Binding Plan and Active Control Map**
- Create a concrete active-control map from this audit so each required backend capability has a visible dashboard button, fetch binding, result pane, disabled/blocked authority proof, and test coverage.
