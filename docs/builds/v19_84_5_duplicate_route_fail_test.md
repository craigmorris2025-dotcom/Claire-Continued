# v19.84.5 Duplicate Route Fail Test

This build enforces the v19.84.4 canonical route registry.

It is intentionally read-only. It does not fix routes. It fails when critical canonical routes are duplicated or missing so the next build can safely target the exact consolidation work needed.

## Commands

```bash
python tools/duplicate_route_fail_test.py
pytest tests/test_v19_84_5_duplicate_route_fail_test.py -q
```

## Output

- `audits/v19_84_5_duplicate_route_fail_test/duplicate_route_fail_test_report.json`
- `audits/v19_84_5_duplicate_route_fail_test/duplicate_route_fail_test_report.md`

## Expected behavior

If current Claire still has duplicate owners, this tool may exit with status code `1`. That is acceptable and useful. It means the failing routes are now known and can be consolidated in v19.84.6.

## Next build

v19.84.6 should demote duplicate owners or restore missing critical routes based only on this report.
