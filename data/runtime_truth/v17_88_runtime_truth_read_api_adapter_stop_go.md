# Claire Syntalion v17.88 — Runtime Truth Read API Adapter

## Status

READY FOR TESTING

## Purpose

v17.88 creates a read-only API adapter for dashboard/search/runtime consumers to access eligible runtime truth through the v17.87 firewall.

## Hard Rules

- Reads only through RuntimeTruthConsumptionFirewall.
- Does not mutate runtime truth.
- Does not ingest evidence.
- Does not promote evidence.
- Does not run live web probes.
- Does not enable automatic updates.
- Does not enable autonomous agent execution.
- Does not allow direct live probe ingestion.

## API Surface

If FastAPI is available, this module exposes:

- GET /runtime-truth/read
- GET /runtime-truth/records

## Stop / Go

GO only if pytest passes and all runtime truth access remains read-only, firewall-mediated, and non-autonomous.
