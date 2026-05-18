# v19.84.9 Cockpit Binding Contract Lock

This build creates the cockpit fetch contract.

It is read-only. It does not rewrite frontend files yet.

## Commands

```bash
python tools/cockpit_binding_contract_lock.py
pytest tests/test_v19_84_9_cockpit_binding_contract_lock.py -q
```

## Output

- `data/cockpit/canonical_cockpit_fetch_contract.json`
- `audits/v19_84_9_cockpit_binding_contract_lock/cockpit_binding_contract_lock.json`
- `audits/v19_84_9_cockpit_binding_contract_lock/cockpit_binding_contract_lock.md`

## Locked principle

The cockpit may render backend truth only. It may not synthesize discoveries, scores, routes, candidates, or narratives locally.

## Next

If no blockers:
- v19.85.0 Evidence Escalation Hardening

If blockers:
- v19.84.10 Cockpit Truth Synthesis Cleanup
