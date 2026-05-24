# Claire Syntalion API Reference

Base URL: `http://localhost:8000`

## Runtime And Dashboard

### GET /dashboard

Primary operator dashboard.

### GET /api/dashboard/state

Canonical dashboard state. This is the dashboard's primary backend-owned truth source.

### GET /api/dashboard/active-control-map

Returns the 19 visible operator controls, their primary endpoints, and the governance flags proving execution/body reads/runtime mutation/command execution are blocked unless explicitly gated.

### GET /dashboard/active-control-map

Dashboard-facing alias for the active control map.

## Lifecycle Route Contracts

### GET /api/lifecycle/center-route-contract

Returns the canonical center route selector: portfolio fallback, threshold fallback, market/acquisition/tech/system-replacement families, and breakthrough fallback.

### GET /api/lifecycle/route-contracts

Returns the five route gate contracts for portfolio, breakthrough, tech design/build, acquisition, and recursive memory.

### POST /api/lifecycle/select-route

Evaluates a payload against the center route contract and returns the selected route, route family, score-gate state, and governance flags.

## Emergence Causal Contracts

### GET /api/emergence/causal-contract

Returns the governed causal bubble, timeline, enabling-condition, similarity, unified-loop, and source-file contract for the 26 uploaded emergence/causal files.

### POST /api/emergence/causal-assess

Evaluates causal emergence conditions and returns momentum, similarity, insufficient-data status, blocked design/CAD guards, and a route vector when multiple valid routes are present.

## Pipeline

### POST /evaluate

Run the governed evaluation pipeline.

```json
{
  "input_text": "Target description text",
  "mode": "deterministic|connected|hybrid",
  "request_type": "evaluate|analyze|plan|construct",
  "source": "api|ui|cli",
  "priority": "low|medium|high"
}
```

### GET /scorecard/{run_id}

Formatted scorecard for a completed run.

### GET /history

Pipeline run history.

### GET /history/{run_id}

Full details for one run.

## Governed Search And Providers

### GET /api/search/providers/status

Provider readiness and configuration status.

### GET /api/search/lane-config

Search lane contract for governed research intake versus external open-search behavior.

### POST /api/search/governed/query/payload

Build a governed query plan.

### POST /api/search/governed/query/actions

Stage governed search actions for review.

## Technology, ACS2, And Re-Emergence

### GET /api/technology/base

Technology base assessment, including ACS2 lineage, root-to-current timelines, predictive trend engine, and re-emergence pattern engine.

### GET /api/technology/search

Searches the local generated technology base.

### GET /api/technology/intelligence

Technology intelligence analysis for a query/domain/route.

### GET /api/technology/reemergence-taxonomy

Returns the route-ready re-emergence taxonomy: 8 primary categories, 7 signal families, 12 re-emergence patterns, timeline engine contract, and attachment-readiness flags.

### GET /api/technology/reemergence-classify

Classifies a query against the re-emergence taxonomy and returns detected patterns, signal-family readiness, category matches, cycle stage, and route guidance.

### GET /api/acs2/graph

ACS2 graph view for a query.

### GET /api/acs2/timeline/{entity_id}

Root-to-current timeline for an ACS2 entity.

### GET /api/acs2/reemergence-taxonomy

ACS2 namespace alias for the re-emergence taxonomy.

## Evidence And Source Governance

### GET /api/evidence/quarantine/cards

Reviewable evidence quarantine cards.

### GET /api/evidence/quarantine/actions

Available evidence review/promotion actions.

### GET /api/source-registry/policy

Source authority and policy state.

## Design And CAD

### GET /design-portal/status

Design Portal runtime status.

### GET /design-portal/contract

Design Portal output contract.

### POST /design-portal/build-from-run

Build reviewable design output from a run.

### GET /cad/intent

CAD intent/readiness. CAD export is intentionally disabled until explicit implementation authority is granted.

## Update Governance

### GET /api/open-web/update-governance/status

Update governance readiness, blocked lanes, review/install status, and owner-gate state.

### POST /api/open-web/update-governance/stage-install

Stage an install/update pack for operator review.

### POST /api/open-web/update-governance/apply-install

Apply a staged install only when owner gates and governance requirements are satisfied.

Automatic update execution remains blocked by default.

## System Proof And Standards

### GET /api/system/endpoint-reconciliation

Reconciles frontend calls, mounted routes, compatibility aliases, and unresolved endpoint drift.

### GET /dashboard/system/endpoint-reconciliation

Dashboard-facing endpoint reconciliation view.

### GET /api/system/dependency-chain-proof

Verifies the dependency-to-dependency path across dashboard, runtime, providers, governed search, evidence, pipeline, portfolio output, design/CAD intent, update governance, endpoint reconciliation, and endpoint standards.

### GET /proof/dependency-chain

Proof-facing alias for dependency chain verification.

### GET /api/system/industry-standard-endpoint-package

Industry standard endpoint package aligned to OpenAPI 3.1, OWASP ASVS/LLM Top 10, NIST AI RMF, ISO/IEC 42001, NIST CSF 2.0, NIST SSDF, SLSA, CycloneDX SBOM, and OpenTelemetry expectations.

### GET /api/system/endpoint-standard-settings

Dashboard settings payload for endpoint standards.

### GET /proof/e2e/summary

Legacy full end-to-end proof mounted through the canonical app. Current status is `GO_WITH_WARNINGS`; warnings disclose governed limits rather than missing route blockers.

### GET /proof/platform-smoke/summary

Platform smoke proof. Current status is `GO_TO_PLATFORM_LAUNCH_HARDENING`.

## Health And Docs

### GET /health

Backend health check.

### GET /docs

Swagger UI.

### GET /redoc

ReDoc.
