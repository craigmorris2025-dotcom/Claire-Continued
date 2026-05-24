# Demo Script

Verified date: 2026-05-24

1. Open the cockpit at `/dashboard`.
2. Show runtime truth from `GET /api/dashboard/state`.
3. Open endpoint proof and show `GET /api/system/endpoint-reconciliation` with zero missing routes.
4. Show `GET /api/system/dependency-chain-proof` and walk the chain from dashboard to governed search, evidence quarantine, pipeline evaluation, portfolio artifact, Design Portal, CAD intent, update governance, and standards package.
5. Open ACS2 activation with `GET /api/pipelines/activation` and show trigger-score-route ownership.
6. Open standards with `GET /api/system/standards-control-map` and show NIST, ISO, OWASP, SBOM, and observability mapped to live controls.
7. Open Design Portal and show `/design-portal/contract`, `/cad/intent`, and `/cad/export-contract`.
8. Close by explaining that CAD export, live provider execution, automatic updates, and runtime truth mutation remain gated.

Demo promise:

No invisible magic. Every visible claim maps to a backend route, a test, and a governance boundary.
