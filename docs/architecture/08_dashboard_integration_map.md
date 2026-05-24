# Dashboard Integration Map

Verified date: 2026-05-24

The dashboard is a command and presentation surface. It does not own runtime truth.

Canonical dashboard surfaces:

- dashboard shell: `GET /dashboard`
- dashboard state: `GET /api/dashboard/state`
- active controls: `GET /api/dashboard/active-control-map`
- runtime truth: `GET /dashboard/runtime-truth`
- endpoint reconciliation: `GET /api/system/endpoint-reconciliation`
- dependency proof: `GET /api/system/dependency-chain-proof`
- standards map: `GET /api/dashboard/standards-control-map`

The v1.0 fetch scan found `458` caller entries and `188` unique frontend endpoints. Reconciliation status is clean:

- `active`: 66
- `stale_alias`: 22
- `duplicate`: 7
- `remove`: 93
- `missing`: 0

Machine artifacts:

- frontend fetch map: `reports/frontend_fetch_map_20260524_v1.txt`
- frontend fetch map JSON: `reports/frontend_fetch_map_20260524_v1.json`
- reconciliation table: `reports/endpoint_reconciliation_20260524_v1.md`
- reconciliation JSON: `reports/endpoint_reconciliation_20260524_v1.json`
- dashboard/backend route manifest: `reports/v1_0_dashboard_backend_route_manifest_20260524.json`

Frozen interpretation:

The dashboard can keep stale aliases only where the backend owns a canonical compatibility route. Any route marked `remove` is not a missing backend contract; it is a cleanup candidate for future UI simplification.
