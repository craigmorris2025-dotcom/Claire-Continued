# System Overview

Verified date: 2026-05-24

Claire is currently locked around the canonical backend app `main.py -> claire.app:create_app`, with the dashboard served from `/dashboard` and backend-owned truth exposed through `/api/dashboard/state`.

Current truth:

- active mounted endpoints: `350`
- canonical dashboard caller entries scanned: `457`
- endpoint reconciliation status: `clean`
- dependency proof status: `clean_e2e_review_proof`
- ACS2 status: `ACS2 trigger-score-route execution map`
- design portal status: `contract_ready`
- CAD intent status: `intent_review_ready`

The cockpit is presentation and command surface only. Backend owners hold runtime truth, route selection, endpoint reconciliation, proof state, design portal contract state, CAD intent, governed evidence, and update governance.

The next layers to attach after this lock are standards and operational overlays: NIST, ISO, OWASP, SBOM, observability, install verification, and cleanup.
