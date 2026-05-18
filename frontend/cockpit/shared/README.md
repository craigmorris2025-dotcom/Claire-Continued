# shared

Purpose:
Shared API client, payload adapter, state store, status models, loading and error states.

Status:
Created in v19.66 as architecture skeleton only.

Rules:
- Do not put source-of-truth runtime logic here.
- Use shared adapters for backend data.
- Register panels through the cockpit panel registry in later builds.
