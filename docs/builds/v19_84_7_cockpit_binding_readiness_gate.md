# v19.84.7 Cockpit Binding Readiness Gate

This build decides whether Claire is allowed to move from route authority consolidation into cockpit binding.

It is read-only and does not change frontend or backend routes.

## Commands

```bash
python tools/cockpit_binding_readiness_gate.py
pytest tests/test_v19_84_7_cockpit_binding_readiness_gate.py -q
```

## Output

- `audits/v19_84_7_cockpit_binding_readiness_gate/cockpit_binding_readiness_gate.json`
- `audits/v19_84_7_cockpit_binding_readiness_gate/cockpit_binding_readiness_gate.md`

## Decision logic

If critical routes are missing or duplicate-mounted, the gate blocks cockpit binding.

If critical route authority is clean, the gate allows:

- `v19.84.8 Cockpit Canonical Fetch Map`

If blocked, the next build should be:

- `v19.84.8 Critical Route Resolution`

## Testing cadence

Minimum gate after install:

```bash
pytest tests/test_v19_84_7_cockpit_binding_readiness_gate.py -q
python tools/cockpit_binding_readiness_gate.py
python main.py
```

Then check:

- `/docs`
- `/dashboard/payload/status`
