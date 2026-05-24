# Design Portal to CAD Chain

Verified date: 2026-05-24

This chain is additive after `v0.9-endpoint-proof-lock`.

Active contract surfaces:

- `GET /design-portal/status`
- `GET /design-portal/output`
- `GET /design-portal/contract`
- `POST /design-portal/build-from-run`
- `GET /cad/intent`
- `GET /cad/export-contract`

Current state:

- Design Portal is contract-ready.
- CAD intent is reviewable.
- CAD export contract is prepared.
- CAD export implementation is intentionally disabled.
- CAD artifact retrieval is not exposed yet.

Required before real CAD export:

- accepted Design Portal contract
- validated blueprint package
- operator export approval
- CAD adapter owner
- artifact retrieval contract

The dashboard may render the intent and export contract, but it may not perform export or mutate runtime truth.
