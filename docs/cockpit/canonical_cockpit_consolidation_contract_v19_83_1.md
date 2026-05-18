# Claire Syntalion v19.83.1 — Canonical Cockpit Consolidation Contract

Generated UTC: 2026-05-11T21:44:13.809021+00:00

## Purpose

Declare the single canonical cockpit architecture before further dashboard/runtime builds.

## Current System Truth

- Manifest entries: 9845
- Python route hits: 287
- Frontend cockpit/dashboard files of interest: 22
- Payload-related files: 692
- Launcher candidates: 4
- Canonical app candidate: `claire/app.py`
- Canonical cockpit shell: `frontend/cockpit/shell/cockpit_shell.html`

## Final Platform Mission

Claire must become a governed autonomous intelligence platform:

signal governance → trend discovery → thesis formation → portfolio/acquisition/breakthrough/design/package routing → validation → final package → lifecycle memory → recursive self-ingestion.

## 30-Stage Lifecycle

1. Signal Ingestion
2. Signal Normalization
3. Source Validation & Weighting
4. Context Expansion
5. Signal Consolidation
6. Entity Extraction
7. Relationship Mapping
8. Trend Discovery
9. Cluster Formation
10. Insight / Thesis Structuring
11. Gap Detection
12. Gap Qualification
13. Discovery Generation
14. Breakthrough Identification & Classification
15. Advancement Path Selection
16. Auto Invention / Solution Generation
17. Solution Structuring
18. Buildability Assessment
19. Viability Assessment
20. Manufacturability / Deployability Assessment
21. Feasibility Validation
22. Design Portal Output / Blueprints / Specs
23. Market Positioning
24. Moat & Differentiation
25. Business Model & Value Capture
26. Competitor Analysis
27. Portfolio Creation / Optimization
28. Acquirer Identification
29. Acquisition Fit & Rationale
30. Final Package Construction

## Protected Stages 16–22

Stages 16–22 are protected and first-class: Auto Invention / Solution Generation; Solution Structuring; Buildability; Viability; Manufacturability / Deployability; Feasibility Validation; Design Portal Output / Blueprints / Specs.

## Canonical Cockpit Contract

- One canonical shell: `frontend/cockpit/shell/cockpit_shell.html`
- One primary payload source: `GET /dashboard/payload`
- Runtime source: `GET /runtime/continuous/status`
- Review queue source: `GET /runtime/continuous/review-queue`
- Source registry: `GET /universes`

Rules:
- Backend owns all runtime truth; cockpit renders only.
- No Swagger, docs, OpenAPI, health control, or endpoint list is exposed in the operator cockpit.
- The cockpit may show unavailable/waiting/empty states, but may not fabricate discoveries, scoring, portfolios, breakthroughs, designs, packages, or route states.

## Canonical Workspaces

- **Runtime** (`runtime`): Manual run state, continuous runtime state, lifecycle state, route state, review counts.
- **Intelligence** (`intelligence`): Signals, governance, trend discovery, cluster formation, thesis formation, gap detection, discovery candidates.
- **Portfolio** (`portfolio`): Portfolio creation, optimization, risk/exposure notes, action recommendations.
- **Breakthrough** (`breakthrough`): Breakthrough identification, classification, category routing, threshold gates.
- **Design** (`design`): Auto Invention, solution structuring, buildability, viability, manufacturability, feasibility, design portal outputs.
- **Acquisition** (`acquisition`): Market positioning, moat, business model, competitor analysis, acquirer mapping, acquisition fit, final package.
- **Sources** (`sources`): Source universes, trust, governance, probes, evidence capture.
- **Review Queue** (`review`): Operator-gated promotion, evidence review, candidate review, governance disposition.
- **System** (`system`): Diagnostics, route availability, payload verification, update governance, regression guard, lifecycle memory.

## Frontend Consolidation Rules

Canonical active frontend:
- `frontend/cockpit/shell/cockpit_shell.html`
- `frontend/cockpit/shell/assets/claire_authored_enterprise_cockpit_shell.css`
- `frontend/cockpit/shell/assets/claire_authored_enterprise_cockpit_shell.js`

May be reused only after review:
- `frontend/cockpit/shared/payload_adapter.js`
- `frontend/cockpit/shared/payload_route_guard.js`
- `frontend/cockpit/runtime/runtime_payload_gate.js`
- `frontend/cockpit/assets/enterprise_cockpit_workspace_shell.js`
- `frontend/cockpit/assets/enterprise_cockpit_continuous_runtime.js`
- `frontend/cockpit/assets/enterprise_cockpit_actions.js`

Must not drive canonical dashboard without review:
- `frontend/command_center/modern/index.html`
- `archive/cockpit_shell_backups/*`
- `_claire_archives/**/frontend/command_center/modern/index.html`

## Build Order From Here

- **v19.83.2 — Active Route Truth Verification Harness**: Create a testable route truth endpoint/audit that proves the running backend returns the cockpit's required payloads.
- **v19.83.3 — Single Payload Adapter Consolidation**: Make authored cockpit use one payload adapter and one fallback policy.
- **v19.83.4 — Continuous Runtime Executor Binding**: Bind continuous runtime buttons and state to the real executor/cycle store.
- **v19.83.5 — Workspace Data Contracts**: Define exact payload contracts per workspace: runtime, intelligence, portfolio, breakthrough, design, acquisition, sources, review, system.
- **v19.83.6 — Legacy Dashboard Quarantine Gate**: Stop noncanonical frontend shells from affecting the operator cockpit.
- **v19.83.7 — Lifecycle Stage Status Renderer**: Render all 30 lifecycle stages with route-aware status, skipped_by_route reasons, evidence, confidence, and terminal state.
- **v19.83.8 — Candidate Review and Promotion Workflow**: Surface candidates and operator review actions without automatic truth mutation.
- **v19.83.9 — Portfolio/Breakthrough/Design/Acquisition Workspace Binding**: Bind downstream workspaces to backend-owned artifacts and empty states.
- **v19.83.10 — Lifecycle Memory and Recursive Self-Ingestion Surface**: Expose memory/replay/self-ingestion status and artifacts.
