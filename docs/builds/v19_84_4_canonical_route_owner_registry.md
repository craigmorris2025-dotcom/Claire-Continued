# v19.84.4 Canonical Route Owner Registry

This build declares route authority. It does not modify mounted routes.

## Commands

```bash
python tools/canonical_route_owner_registry.py
pytest tests/test_v19_84_4_canonical_route_owner_registry.py -q
```

## Primary output

- `data/runtime_authority/canonical_route_owner_registry.json`
- `audits/v19_84_4_canonical_route_owner_registry/canonical_route_owner_registry_report.json`
- `audits/v19_84_4_canonical_route_owner_registry/canonical_route_owner_registry_report.md`

## Authority rules locked

- Backend owns truth.
- Cockpit owns presentation only.
- One owner per critical method/path route is required.
- Compatibility layers must delegate to canonical owners.
- Empty, pending, unavailable, and insufficient-evidence states are valid.
- Operator review is required before promotion.

## Next build

v19.84.5 should add an enforcing duplicate-route fail test against this registry.
