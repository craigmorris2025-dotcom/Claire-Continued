# v19.84.8 Cockpit Canonical Fetch Map

This build inventories cockpit/frontend fetch dependencies and maps them to canonical backend-owned routes.

It is read-only and does not rewrite cockpit behavior.

## Commands

```bash
python tools/cockpit_canonical_fetch_map.py
pytest tests/test_v19_84_8_cockpit_canonical_fetch_map.py -q
```

## Output

- `audits/v19_84_8_cockpit_canonical_fetch_map/cockpit_canonical_fetch_map.json`
- `audits/v19_84_8_cockpit_canonical_fetch_map/cockpit_canonical_fetch_map.md`

## Purpose

Prevent:
- frontend truth synthesis,
- hidden mock payloads,
- dashboard/backend drift,
- duplicate fetch ownership.

This build prepares for:
- cockpit canonical binding lock,
- runtime-to-cockpit synchronization,
- enterprise cockpit stabilization.
