# Enterprise Cockpit Architecture v19.64

Generated: 2026-05-11T09:28:48.103288Z

- Decision: Retire scaling of old dashboard; build new enterprise cockpit from mapped active systems.
- New root: `frontend/cockpit/`
- Legacy dashboard rule: Existing dashboard remains legacy/reference until payload, runtime, search, and operator parity are proven.

## Backend Surface Inputs

| Surface | Routes | Owners | Feeds Modules |
|---|---:|---:|---|
| `boot_health` | 64 | 56 | shell, system |
| `dashboard_payload` | 8 | 127 | shared, runtime, intelligence, design, package, system |
| `runtime_lifecycle` | 27 | 262 | runtime |
| `search_provider` | 22 | 409 | intelligence |
| `governed_web_probe` | 25 | 297 | intelligence, system |
| `runtime_truth_evidence` | 0 | 94 | runtime, system |

## Permanent Search Panel Rule

- Status: core architecture requirement
- Placement: top-level command surface, not optional panel-only search

Capabilities:
- normal web search interface
- governed internet research interface
- runtime/project search
- lifecycle navigation and command recognition
- future AI-agent command entry
