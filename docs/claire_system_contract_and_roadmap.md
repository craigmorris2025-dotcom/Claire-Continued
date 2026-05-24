# Claire System Contract and Roadmap

This document organizes the uploaded pipeline notes and complete-system HTML into the working route contract for Claire. It is the product-facing roadmap for continued cleanup: code should converge toward this shape, and tests should prove each path works before dashboard wiring is treated as real.

## Source Materials

Primary order of authority:

1. `Final Endgame Pipeline.txt`
2. `Branching Master Pipeline.txt`
3. `Core Pipeline Architecture.txt`
4. `Minimal Completed-State Pipeline.txt`
5. `Lifecycle Spine.txt`
6. `Governance  Fail-Safe Pipeline.txt`
7. `(7)Claire-Complete-Systems-Flow .html`
8. Route-specific notes:
   - `trends 2 portfolio.txt`
   - `trend to breakthrough.txt`
   - `trend 3 acquisition.txt`
   - `Full Breakthrough-to-Acquisition Package Pipeline.txt`
   - `portfolio and optimization.txt`
   - `Recursive Learning Pipeline.txt`
   - `Existing System Ingestion  Replacement Pipeline.txt`
   - `Breakthrough categories.txt`
   - `Claire Enterprise Online Update Governance System.txt`

## Runtime Model

Claire is one runtime. It does not run separate disconnected products for portfolio, design, acquisition, and memory.

All runs begin with the shared signal spine:

1. Signal Ingestion
2. Signal Normalization
3. Source Validation and Weighting
4. Context Expansion
5. Signal Consolidation
6. Entity Extraction
7. Relationship Mapping
8. Trend Discovery
9. Cluster Formation
10. Insight / Thesis Structuring

After Stage 10, route selection is decided by signals, source authority, scores, and gates:

- Portfolio is the default working path.
- Breakthrough/design is conditional and activates only when gap, breakthrough, synthesis, confidence, and source conditions are met.
- Acquisition is strategic and activates when acquisition/deal-fit signals are present.
- Lifecycle memory feeds verified prior outputs back into Stage 1 as context only.

## Canonical Paths

The code source of truth is `claire/lifecycle/canonical_paths.py`.

### Portfolio Creation / Optimization

Used when a trend/thesis is actionable but does not meet breakthrough or acquisition activation conditions.

Path:

1-10 shared spine, then:

- 23 Market Positioning
- 26 Competitor Analysis
- 27 Portfolio Creation / Optimization
- 30 Final Package Construction

Expected output:

- portfolio action
- portfolio thesis
- risk and exposure notes
- action recommendations
- final package

### Breakthrough / Design

Used when runtime signals satisfy breakthrough activation conditions. Design activation can come from explicit route recommendation or from live signal conditions that meet thresholds.

Path:

1-10 shared spine, then:

- 11 Gap Detection
- 12 Gap Qualification
- 13 Discovery Generation
- 14 Breakthrough Identification and Classification
- 15 Advancement Path Selection
- 16 Auto Invention / Solution Generation
- 17 Solution Structuring
- 18 Buildability Assessment
- 19 Viability Assessment
- 20 Manufacturability / Deployability Assessment
- 21 Feasibility Validation
- 22 Design Portal Output / Blueprints / Specs
- 23 Market Positioning
- 24 Moat and Differentiation
- 25 Business Model and Value Capture
- 26 Competitor Analysis
- 27 Portfolio Creation / Optimization
- 28 Acquirer Identification
- 29 Acquisition Fit and Rationale
- 30 Final Package Construction

Expected output:

- breakthrough classification
- design portal activation truth
- blueprint/spec output
- feasibility and buildability basis
- acquisition/package continuation when fit exists
- final package

### Acquisition Package

Used when signals indicate strategic acquisition opportunity or deal-fit logic.

Path:

1-10 shared spine, then:

- 11 Gap Detection
- 12 Gap Qualification
- 23 Market Positioning
- 24 Moat and Differentiation
- 25 Business Model and Value Capture
- 26 Competitor Analysis
- 28 Acquirer Identification
- 29 Acquisition Fit and Rationale
- 30 Final Package Construction

Expected output:

- acquirer list
- fit rationale
- value-capture and moat basis
- acquisition-ready package

## Governance Rules

- Route is selected by signals received and conditions met during runtime.
- Breakthrough capability must always exist, but breakthrough stages are only required when the branch activates.
- Design portal output is required only for design/system/software routes.
- Prior Claire output is not live truth. It may seed Stage 1 context and pattern comparison only.
- Runtime dashboard truth must display the selected route, evidence, completion gate, memory status, and source authority.
- A dashboard route is not real until the backend route works and tests prove it.

## Current Code Alignment

Implemented main path owners:

- `claire/lifecycle/canonical_paths.py` stores the canonical route paths.
- `claire/lifecycle/lifecycle_runner.py` selects route-aware lifecycle contracts.
- `claire/lifecycle/stage_contracts.py` requires stages based on the selected route path.
- `claire/design/portal.py` activates design from explicit recommendations or strong live breakthrough signals.
- `claire/memory/lifecycle_memory_signal.py` re-ingests eligible prior outputs into Stage 1 as governed context.
- `/evaluate` writes route and lifecycle truth used by `/api/dashboard/state`.
- `claire/api/canonical_route_manifest.py` mounts the active app route family.
- `/api/dashboard/active-control-map` exposes 19 backend-owned dashboard controls.
- `/api/system/endpoint-reconciliation` proves stale menu/frontend calls are either mounted, aliased, or unresolved.
- `/api/system/dependency-chain-proof` proves the dashboard-to-runtime-to-provider-to-pipeline-to-output-to-update-governance dependency path.
- `/api/system/industry-standard-endpoint-package` defines the endpoint expectations against industry standard API, security, AI governance, supply-chain, SBOM, and telemetry practices.
- `/design-portal/contract`, `/design-portal/status`, and `/cad/intent` expose review-ready design/CAD status; CAD export remains disabled until explicit authority is granted.
- `/api/lifecycle/center-route-contract` exposes the center route selector from the operator route files.
- `/api/lifecycle/route-contracts` exposes portfolio, breakthrough, tech design/build, acquisition, and recursive memory route gates.
- `/api/lifecycle/select-route` evaluates a payload against the center route contract without mutating runtime truth.
- `/api/technology/reemergence-taxonomy` exposes the 8 primary categories, 7 signal families, and 12 re-emergence patterns from the operator category/timeline notes.
- `/api/technology/reemergence-classify` classifies a query against the re-emergence taxonomy for route-ready emergence intake.
- Update governance routes expose review/stage/apply install flows while blocking automatic execution by default.

## Current Proof State

Verified on 2026-05-23:

- Mounted routes: `350`
- Endpoint reconciliation: `clean`
- Dependency chain proof: `clean_e2e_review_proof`
- Platform smoke proof: `GO_TO_PLATFORM_LAUNCH_HARDENING`
- Full end-to-end proof pack: `GO_WITH_WARNINGS`

The `GO_WITH_WARNINGS` state is acceptable for cleanup/consolidation review because the warnings disclose intentional governance limits, not missing route blockers: live provider execution requires configured provider credentials and owner gates, and CAD/buildability final packaging remains review-only.

## Causal Engine Intake

- `/api/emergence/causal-contract` exposes the governed causal bubble, timeline, enabling-condition, similarity, unified-loop, and source-file contract for the 26 uploaded emergence/causal files.
- `/api/emergence/causal-assess` evaluates causal emergence conditions, blocked design/CAD guards, insufficient-data behavior, and route-vector output when multiple valid routes are present.
- Causal runtime truth mutation and route truth mutation remain blocked by default; operator review is required before deeper runtime promotion.

## Proof Tests

Current regression tests that protect this contract:

- `tests/test_canonical_lifecycle_paths.py`
- `tests/test_signal_condition_routes.py`
- `tests/test_lifecycle_memory_signal.py`
- `tests/test_runtime_wiring_reality.py`
- `tests/test_s1323_s1350_dashboard_active_control_map.py`
- `tests/test_endpoint_reconciliation_compat.py`
- `tests/test_dependency_chain_proof.py`
- `tests/test_industry_standard_endpoint_package.py`
- `tests/test_legacy_proof_routes_current_canonical.py`

## Cleanup Direction

Future cleanup should follow this rule:

When code conflicts with this contract, replace the old path with a clean canonical owner, update tests to prove the intended behavior, and remove bridge/drift files only after behavior is preserved.
