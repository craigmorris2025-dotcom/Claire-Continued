# Claire v17.42 — Internet Runtime Integration

This package integrates the working v17.41 internet activation core into Claire runtime outputs.

## Adds

- InternetRuntimeBridge
- InternetLifecycleAdapter
- CoreRunOutputInternetMerger
- InternetEvidenceContinuityStore
- InternetDashboardPayloadBuilder
- InternetRuntimeIntegrationService
- FastAPI routes: POST /runtime/internet/enrich and POST /runtime/internet/dashboard

## Boundary

This package does not rewrite unknown dashboard component files automatically.
It provides a stable dashboard payload for the Research tab to consume.
It does not perform unrestricted browsing. It uses the v17.41 governed internet service.
