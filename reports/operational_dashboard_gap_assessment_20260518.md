# Claire Operational Dashboard Gap Assessment

Date: 2026-05-18

## Executive Finding

The current Claire system is operational at the local FastAPI/TestClient level and is at the governed internet-connectivity threshold. It is not correctly represented by the dashboard yet.

The dashboard problem is not visual quality. The problem is operational parity:

- backend files and routes have advanced faster than the dashboard.
- key cockpit routes existed in code but were not mounted.
- the dashboard had become partly endpoint-map/presentation oriented.
- operator actions were displayed but not reliably connected to governed backend result previews.
- the cockpit does not yet provide a complete workbench for operating Claire across lifecycle, evidence, live-web gates, portfolio, acquisition, design, memory, runtime, and cleanup readiness.

## Verified Working Now

Environment:

- `.venv` rebuilt.
- pinned `requirements.txt` installed.

Routes verified:

- `/dashboard` returns active dashboard v3 HTML.
- `/dashboard/payload` returns the full backend-owned payload, about 222 KB.
- `/dashboard/endpoint-map` returns the 595-endpoint route map.
- `/dashboard/operator-action/result/plan_search` returns governed review-only action output.
- `/api/governed/live-probe/status` returns registered governed live-probe status.
- `/api/cockpit/surface-registry` now returns the cockpit surface registry.
- `/api/cockpit/surface-health` now returns cockpit surface health.

Test verification:

- `tests/test_s1125_s1152_operator_action_click_result_bridge.py`
- `tests/test_s1626_s1650_dashboard_v3_legacy_contract_bridge.py`
- `tests/test_s1501_s1600_endpoint_mapped_dashboard_v3.py`
- `tests/test_s36_governed_live_probe_contracts.py`

Result:

- 20 passed.

## Repairs Made In This Pass

1. `frontend/command_center/modern/index.html`
   - Mounted `operator_action_click_bridge.css` in active dashboard v3.

2. `frontend/command_center/modern/operator_action_click_bridge.js`
   - Converted the bridge from click-count-only behavior into a governed GET-only action preview client.
   - It calls `/dashboard/operator-action/result/{action_key}`.
   - It renders review result, next step, and blocked authority state.
   - It preserves blocked language for web execution and body reads.
   - It does not use POST or mutation behavior.

3. `claire/app.py`
   - Mounted missing cockpit surface registry routes explicitly.
   - Mounted missing cockpit surface health routes explicitly.
   - Avoided broad `register_*_routes` auto-discovery because that causes older dashboard modules to seize `/dashboard/payload`.

## Critical Dashboard Problems Found

### 1. The Dashboard Is Not Yet The True System Operator

The backend payload already exposes:

- 30 lifecycle stages.
- 12 dashboard panels.
- 132 operator surface routes.
- governed web safety locks.
- live-probe status.
- update governance locks.
- portfolio/breakthrough/design/acquisition panels.
- source universes and evidence review concepts.

But the dashboard does not yet make these into a coherent operating workflow.

### 2. Route Mount Drift Exists

Some modules define route registration functions named `register_*_routes`, while app discovery only included `include_*_routes`. This left real cockpit surfaces unmounted.

Fixed for:

- cockpit surface registry.
- cockpit surface health.

Still needs audit for other unmounted operational modules.

### 3. Duplicate Dashboard Payload Ownership Exists

There are multiple `/dashboard/payload` route owners in the codebase. A broad route-registration pass can make an older/smaller dashboard payload override the full backend-owned payload.

This is a serious operational integrity problem. The system needs one canonical payload owner and explicit aliases only.

### 4. Dashboard V3 Is Endpoint-Map Heavy

The endpoint map is useful, but a real cockpit needs task-oriented operation:

- What mode is Claire in?
- What stage is active?
- What evidence is missing?
- What is blocked and why?
- What is ready for operator approval?
- What route should be run next?
- What file/folder/data state is required for that action?
- What changed since last run?
- What is safe to clean/archive?

### 5. Live Web Is Ready-Adjacent, Not Freely Live

The current posture is correct:

- live probe route registered.
- live execution blocked by default.
- HEAD-only probe requires explicit operator trigger.
- body reads blocked.
- runtime mutation blocked.
- automatic updates blocked.

The dashboard must make this visible as an operational control system, not a vague status badge.

### 6. File/Folder Operational Readiness Is Missing From The Dashboard

Your cleanup concern is connected to the dashboard concern. The dashboard should know whether the required folders/files are present and current:

- `claire/`
- `frontend/`
- future `backend/`
- `data/runtime`
- `data/memory`
- `data/source_universes`
- `runtime/governed_live_probe`
- `output/dashboard_endpoint_map`
- `tests/`
- `tools/`
- required docs/config/launchers

It should also expose pollution state:

- `exports/`
- `archive/`
- `backups/`
- `quarantine_legacy_placeholders/`
- `__pycache__/`
- `.pytest_cache/`
- duplicate installers.

## Required Modern Operational Cockpit

Claire needs a sophisticated dashboard with these zones:

1. Command Center
   - system mode
   - active route
   - next safe operator action
   - readiness summary
   - blocked authority matrix

2. Lifecycle Console
   - 30-stage spine
   - current stage
   - stage inputs/outputs
   - missing evidence
   - terminal state

3. Governed Web Console
   - provider status
   - source registry
   - metadata-only probe gate
   - quarantine queue
   - body-read lock
   - one-shot operator trigger readiness

4. Evidence & Source Workbench
   - evidence baskets
   - lineage
   - source trust
   - conflicts
   - manual promotion queue

5. Portfolio & Acquisition Console
   - thesis graph
   - opportunity landscape
   - portfolio optimization
   - acquirer map
   - acquisition rationale
   - package readiness

6. Breakthrough & Design Console
   - gap detection
   - breakthrough classification
   - advancement path
   - buildability/viability/manufacturability/feasibility
   - design portal outputs

7. Runtime & Memory Console
   - run history
   - continuous runtime status
   - recursive learning state
   - replay/comparison

8. System Integrity & Cleanup Console
   - canonical folder/file health
   - duplicate route owners
   - stale installers
   - generated cache count
   - archive candidates
   - cleanup approval queue

## Completion Recommendation

Before large cleanup moves, build and verify the cockpit as the operational authority viewer.

Recommended sequence:

1. Lock canonical payload ownership.
2. Add a dashboard operational parity test that checks every required cockpit surface has a mounted route and rendered frontend region.
3. Build the modern cockpit around backend payload sections, not static dashboard copy.
4. Add file/folder readiness route and panel.
5. Add route-owner/duplicate-route diagnostic panel.
6. Add live-web readiness and one-shot probe control panel.
7. Add cleanup approval panel.
8. Only then perform root cleanup/restructure, with dashboard proving the system still sees all required folders/files.
