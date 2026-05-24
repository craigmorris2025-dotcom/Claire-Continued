# System Overview

Verified date: 2026-05-24

Claire is currently locked around the canonical backend app `main.py -> claire.app:create_app`, with the dashboard served from `/dashboard` and backend-owned truth exposed through `/api/dashboard/state`.

Current truth:

- active mounted endpoints: `353`
- frontend caller entries scanned: `458`
- endpoint reconciliation status: `clean`
- dependency proof status: `clean_e2e_review_proof`
- ACS2 status: `ACS2 trigger-score-route execution map`
- design portal status: `contract_ready`
- CAD intent status: `intent_review_ready`
- CAD export contract status: `contract_prepared_export_disabled`
- standards control map status: `ready`

The cockpit is presentation and command surface only. Backend owners hold runtime truth, route selection, endpoint reconciliation, proof state, design portal contract state, CAD intent, governed evidence, and update governance.

The v1.0 hardening pass freezes the additive layers above the v0.9 proof lock: standards controls, safe cockpit cleanup, Design Portal to CAD contract, product narrative, and Proteus identity.
