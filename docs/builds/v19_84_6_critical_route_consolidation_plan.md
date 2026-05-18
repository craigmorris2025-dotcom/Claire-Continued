# v19.84.6 Critical Route Consolidation Plan

This build is a safe planning build after the duplicate-route fail test.

It reads the canonical route owner registry and the v19.84.5 duplicate-route report, then produces an exact action plan for missing or duplicate critical routes.

## Commands

```bash
python tools/critical_route_consolidation_plan.py
pytest tests/test_v19_84_6_critical_route_consolidation_plan.py -q
```

## Output

- `audits/v19_84_6_critical_route_consolidation_plan/critical_route_consolidation_plan.json`
- `audits/v19_84_6_critical_route_consolidation_plan/critical_route_consolidation_plan.md`

## Why this exists

This prevents blind route edits. If routes are duplicated or missing, v19.84.7 should target only the exact routes listed in this report.

## Testing cadence

For v19.84.x authority builds:
1. install script
2. build-specific pytest
3. backend boot
4. `/docs`
5. `/dashboard/payload/status`
6. route-specific tool/report
