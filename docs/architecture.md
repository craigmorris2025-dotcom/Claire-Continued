# Claire Syntalion Architecture Guide

## Overview

Claire Syntalion is a governed lifecycle intelligence platform built on the CLAIRE cognitive architecture. It processes unstructured input through a shared signal spine, route-aware lifecycle stages, governed web/provider intake, portfolio/acquisition/design outputs, recursive memory, and operator-reviewed update governance.

## Current Runtime Truth

- Active app: `main.py` -> `claire.app:create_app`
- Route manifest: `claire/api/canonical_route_manifest.py`
- Mounted route count verified on 2026-05-23: `350`
- Primary dashboard: `/dashboard`
- Dashboard state: `GET /api/dashboard/state`
- Active control map: `GET /api/dashboard/active-control-map`, 19 controls
- Endpoint reconciliation: `GET /api/system/endpoint-reconciliation`
- Dependency proof: `GET /api/system/dependency-chain-proof`
- Industry standard endpoint package: `GET /api/system/industry-standard-endpoint-package`
- Center route contract: `GET /api/lifecycle/center-route-contract`
- Route contracts: `GET /api/lifecycle/route-contracts`
- Route selector: `POST /api/lifecycle/select-route`
- Re-emergence taxonomy: `GET /api/technology/reemergence-taxonomy`
- Re-emergence classifier: `GET /api/technology/reemergence-classify`

The backend owns runtime truth. Frontend controls render backend contracts and may not fabricate readiness, route availability, proof status, provider readiness, update installation status, or design/CAD completion.

## Cognitive Architecture

The original CLAIRE core remains a 4-phase cognitive pipeline.

### Phase 1: Contract Layer

- `ClaireIntent` validates and structures incoming requests.
- `ContractValidator` enforces schema rules.
- Data flows through typed contracts where local modules support them.

### Phase 2: Orreadir Layer

- `OrreadirRouter` routes requests by type.
- Priority signals and mode constraints influence engine selection.
- Route decisions include stage and engine selection hints.

### Phase 3: Core Processing

- Planning generates strategy-specific execution plans.
- Data engines and semantic layers load profile/evidence context.
- Output builders format JSON, summary, dashboard, and export artifacts.

### Phase 4: Orchestrator

- `PipelineOrchestrator` runs the active lifecycle/engine path.
- Pattern, scoring, validation, and package modules contribute route-specific output.
- MasterPass-style handoff normalizes, asserts, persists, and exposes outputs.

## Lifecycle Contract

The original 24-engine evaluation pipeline remains present, but the active platform is governed by the 30-stage lifecycle contract in `docs/claire_system_contract_and_roadmap.md`. Route selection determines whether portfolio, breakthrough/design, acquisition, package, and memory stages are required for a run.

## Operating Modes And Gates

| Mode | Description | Capabilities |
|------|-------------|--------------|
| Deterministic | Air-gapped/review-safe | Local data and existing governed artifacts only |
| Connected | Governed live/provider lane | External provider metadata can be staged when credentials and gates are configured |
| Hybrid | Full reviewed workflow | Local runtime plus governed external intake, with promotion/update mutation still operator-gated |

Live web execution, body reads, automatic update application, runtime mutation, and autonomous execution are blocked by default. Update/install endpoints exist for review/stage/apply flows, but owner gates decide execution.

## Data Flow

```text
Input Text -> Contract Validation -> Orreadir Routing -> Planning
  -> Semantic Analysis -> Lifecycle/Engine Pipeline
  -> Route Selection -> Portfolio/Design/Acquisition/Package Outputs
  -> Evidence/Provider Governance -> Score Calibration
  -> MasterPass Bridge -> Persistence -> Dashboard/API Response
  -> Proof/Reconciliation/Update Governance
```

## Technology Stack

- Backend: Python 3.12, FastAPI, Pydantic/dataclass contracts, local JSON/SQLite-style persistence where present
- Frontend: HTML5, CSS, vanilla JavaScript, backend-owned dashboard state
- Architecture: canonical route manifest, modular routers, operator-gated update governance, compatibility aliases for stale reviewed surfaces

## Consolidation Status

- Endpoint reconciliation is clean with compatibility aliases for stale valuable frontend calls.
- Dependency-to-dependency proof is clean across dashboard state, active controls, runtime, providers, governed search, evidence, pipeline, portfolio output, design/CAD intent, update governance, endpoint reconciliation, and endpoint standards.
- Full proof pack is `GO_WITH_WARNINGS`; warnings disclose intentional governance limits rather than missing route blockers.
- Causal engine intake is contract-ready through governed emergence causal endpoints; runtime truth mutation and route truth mutation remain blocked by default.
