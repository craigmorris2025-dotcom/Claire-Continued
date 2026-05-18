# Claire Syntalion Symptom Report

- Created: 2026-05-15T18:38:37.871509+00:00
- Root: `C:\Users\craig\OneDrive\Desktop\Claire`
- Target module: `claire.api.governed_cockpit_payload_visibility_s149_s155`
- Imported file: `C:\Users\craig\OneDrive\Desktop\Claire\claire\api\governed_cockpit_payload_visibility_s149_s155.py`
- Target test: `tests\test_s149_s155_live_payload_visibility.py`

## Candidate Module Files
- `claire\api\governed_cockpit_payload_visibility_s149_s155.py` size=6315 modified=2026-05-15T18:29:30.576674+00:00
- `src\claire\api\governed_cockpit_payload_visibility_s149_s155.py` size=6315 modified=2026-05-15T18:29:30.577676+00:00

## Function Result Summary
### build_cockpit_payload_read_contract
- exists: `True`
- call_ok: `True`
- signature: `() -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S149", "status": "cockpit_payload_read_contract_ready", "ok": true}`

### build_live_payload_visibility_probe
- exists: `True`
- call_ok: `True`
- signature: `() -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S150", "status": "live_payload_visibility_probe_ready", "ok": true}`

### build_existing_payload_nonbreak_probe
- exists: `True`
- call_ok: `True`
- signature: `() -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S151", "status": "existing_payload_nonbreak_probe_ready", "ok": true}`

### build_repeated_payload_fetch_stability_probe
- exists: `True`
- call_ok: `True`
- signature: `(fetch_count: 'int' = 3, **_: 'Any') -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S152", "status": "repeated_payload_fetch_stability_probe_ready", "ok": true, "fetch_count": 3}`

### build_cockpit_payload_manifest
- exists: `True`
- call_ok: `True`
- signature: `() -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S153", "status": "cockpit_payload_manifest_ready", "ok": true}`

### build_cockpit_live_visibility_readiness
- exists: `True`
- call_ok: `True`
- signature: `() -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S154", "status": "cockpit_live_visibility_readiness_ready", "ok": true}`

### build_s149_s155_stop_gate
- exists: `True`
- call_ok: `True`
- signature: `(report_dir: 'str | Path | None' = None, **_: 'Any') -> 'Dict[str, Any]'`
- key return fields: `{"stage_version": "S155", "status": "s149_s155_stop_gate_passed", "ok": true, "stop_go": "GO", "safe_to_continue": true, "report_path": "C:\\Users\\craig\\OneDrive\\Desktop\\Claire\\diagnostics\\symptom_reports\\tmp_stop_gate_probe\\s149_s155_stop_gate.json"}`

## Test Imports
- line 1: from `__future__` import `annotations`
- line 3: from `pathlib` import `Path`
- line 5: from `claire.api.governed_cockpit_payload_visibility_s149_s155` import `build_cockpit_payload_read_contract, build_live_payload_visibility_probe, build_existing_payload_nonbreak_probe, build_repeated_payload_fetch_stability_probe, build_cockpit_payload_manifest, build_cockpit_live_visibility_readiness, build_s149_s155_stop_gate`

## Test Assertions
- line 17: `assert contract["stage_version"] == "S149"`
- line 18: `assert contract["status"] == "cockpit_payload_read_contract_ready"`
- line 19: `assert contract["payload_key"] == "governed_operations"`
- line 20: `assert contract["read_only"] is True`
- line 24: `assert probe["stage_version"] == "S150"`
- line 25: `assert probe["ok"] is True`
- line 26: `assert "runtime_spine" in probe["visible_panel_keys"]`
- line 27: `assert "review_export" in probe["visible_panel_keys"]`
- line 31: `assert probe["stage_version"] == "S151"`
- line 32: `assert probe["ok"] is True`
- line 33: `assert probe["rules"]["governed_operations_appended_only"] is True`
- line 34: `assert probe["rules"]["app_py_patch_performed"] is False`
- line 38: `assert probe["stage_version"] == "S152"`
- line 39: `assert probe["ok"] is True`
- line 40: `assert probe["stable_top_level_keys"] is True`
- line 41: `assert probe["stable_panel_keys"] is True`
- line 45: `assert manifest["stage_version"] == "S153"`
- line 46: `assert manifest["status"] == "cockpit_payload_manifest_ready"`
- line 47: `assert manifest["panel_count"] >= 4`
- line 51: `assert readiness["stage_version"] == "S154"`
- line 52: `assert readiness["ok"] is True`
- line 53: `assert readiness["checks"]["runtime_truth_write_blocked"] is True`
- line 57: `assert report["stage_version"] == "S155"`
- line 58: `assert report["ok"] is True`
- line 59: `assert report["forward_motion_allowed"] is True`
- line 60: `assert report["remaining_countdown"]["packs_remaining_after_this"] == 3`
- line 61: `assert Path(report["report_path"]).exists()`

## Pytest Target Result
- returncode: `1`
```text
FFFFFFF                                                                  [100%]
================================== FAILURES ===================================
________________________ test_s149_read_contract_ready ________________________

    def test_s149_read_contract_ready():
        contract = build_cockpit_payload_read_contract()
        assert contract["stage_version"] == "S149"
        assert contract["status"] == "cockpit_payload_read_contract_ready"
>       assert contract["payload_key"] == "governed_operations"
               ^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'payload_key'

tests\test_s149_s155_live_payload_visibility.py:19: KeyError
______________________ test_s150_visibility_probe_passes ______________________

    def test_s150_visibility_probe_passes():
        probe = build_live_payload_visibility_probe()
        assert probe["stage_version"] == "S150"
        assert probe["ok"] is True
>       assert "runtime_spine" in probe["visible_panel_keys"]
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'visible_panel_keys'

tests\test_s149_s155_live_payload_visibility.py:26: KeyError
__________________ test_s151_existing_payload_nonbreak_probe __________________

    def test_s151_existing_payload_nonbreak_probe():
        probe = build_existing_payload_nonbreak_probe()
        assert probe["stage_version"] == "S151"
        assert probe["ok"] is True
>       assert probe["rules"]["governed_operations_appended_only"] is True
               ^^^^^^^^^^^^^^
E       KeyError: 'rules'

tests\test_s149_s155_live_payload_visibility.py:33: KeyError
_____________________ test_s152_repeated_fetch_stability ______________________

    def test_s152_repeated_fetch_stability():
        probe = build_repeated_payload_fetch_stability_probe(fetch_count=3)
        assert probe["stage_version"] == "S152"
        assert probe["ok"] is True
>       assert probe["stable_top_level_keys"] is True
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'stable_top_level_keys'

tests\test_s149_s155_live_payload_visibility.py:40: KeyError
______________________ test_s153_payload_manifest_ready _______________________

    def test_s153_payload_manifest_ready():
        manifest = build_cockpit_payload_manifest()
        assert manifest["stage_version"] == "S153"
        assert manifest["status"] == "cockpit_payload_manifest_ready"
>       assert manifest["panel_count"] >= 4
               ^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'panel_count'

tests\test_s149_s155_live_payload_visibility.py:47: KeyError
_____________________ test_s154_live_visibility_readiness _____________________

    def test_s154_live_visibility_readiness():
        readiness = build_cockpit_live_visibility_readiness()
        assert readiness["stage_version"] == "S154"
        assert readiness["ok"] is True
>       assert readiness["checks"]["runtime_truth_write_blocked"] is True
               ^^^^^^^^^^^^^^^^^^^
E       KeyError: 'checks'

tests\test_s149_s155_live_payload_visibility.py:53: KeyError
_________________________ test_s155_stop_gate_passes __________________________

tmp_path = WindowsPath('C:/Users/craig/AppData/Local/Temp/pytest-of-craig/pytest-158/test_s155_stop_gate_passes0')

    def test_s155_stop_gate_passes(tmp_path: Path):
        report = build_s149_s155_stop_gate(report_dir=tmp_path / "reports")
        assert report["stage_version"] == "S155"
        assert report["ok"] is True
>       assert report["forward_motion_allowed"] is True
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'forward_motion_allowed'

tests\test_s149_s155_live_payload_visibility.py:59: KeyError
=========================== short test summary info ===========================
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s149_read_contract_ready
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s150_visibility_probe_passes
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s151_existing_payload_nonbreak_probe
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s152_repeated_fetch_stability
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s153_payload_manifest_ready
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s154_live_visibility_readiness
FAILED tests/test_s149_s155_live_payload_visibility.py::test_s155_stop_gate_passes


```

## Import Debug
```text
FILE= C:\Users\craig\OneDrive\Desktop\Claire\claire\api\governed_cockpit_payload_visibility_s149_s155.py
S149= {'stage_version': 'S149', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'contract_id': 'cockpit_payload_read_contract', 'status': 'cockpit_payload_read_contract_ready', 'ok': True}
S150= {'stage_version': 'S150', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'probe_id': 'live_payload_visibility_probe', 'status': 'live_payload_visibility_probe_ready', 'ok': True, 'live_payload_visibility': True, 'dashboard_payload_visible': True, 'payload_status_visible': True}
S151= {'stage_version': 'S151', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'probe_id': 'existing_payload_nonbreak_probe', 'status': 'existing_payload_nonbreak_probe_ready', 'ok': True, 'preserves_existing_payload': True, 'nonbreaking': True, 'mutates_payload': False, 'writes_runtime_truth': False}
S152= {'stage_version': 'S152', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'probe_id': 'repeated_payload_fetch_stability_probe', 'status': 'repeated_payload_fetch_stability_probe_ready', 'ok': True, 'fetch_count': 3, 'repeated_fetch_stable': True, 'all_fetches_consistent': True}
S153= {'stage_version': 'S153', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'manifest_id': 'cockpit_payload_manifest', 'status': 'cockpit_payload_manifest_ready', 'ok': True, 'payload_fragments': ['cockpit_payload_read_contract', 'live_payload_visibility_probe', 'existing_payload_nonbreak_probe', 'repeated_payload_fetch_stability_probe', 'cockpit_live_visibility_readiness', 's149_s155_stop_gate']}
S154= {'stage_version': 'S154', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'readiness_id': 'cockpit_live_visibility_readiness', 'status': 'cockpit_live_visibility_readiness_ready', 'ok': True, 'live_visibility_ready': True, 'dashboard_ready': True, 'payload_ready': True}
S155= {'stage_version': 'S155', 'backend_owns_truth': True, 'cockpit_presentation_only': True, 'read_only': True, 'allowed_methods': ['GET'], 'required_endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'endpoints': ['/dashboard/payload', '/dashboard/payload/status', '/health'], 'manual_promotion_required': True, 'quarantine_required': True, 'runtime_truth_write_enabled': False, 'runtime_mutation_enabled': False, 'automatic_updates_enabled': False, 'autonomous_execution_enabled': False, 'continuous_crawling_enabled': False, 'gate_id': 's149_s155_stop_gate', 'status': 's149_s155_stop_gate_passed', 'ok': True, 'stop_go': 'GO', 'passed': True, 'safe_to_continue': True}


```

## Forward Motion / Lock Flag Samples
### `claire\acquirers\dataset.py`
- hits: `GO`
  - L53: `                "ticker": "GOOGL",`
### `claire\api\allowlist_rate_limit_enforcement_proof.py`
- hits: `automatic_updates, autonomous_execution`
  - L50: `        "autonomous_execution": "blocked",`
  - L51: `        "automatic_updates": "blocked",`
### `claire\api\canonical_browser_session_persistence.py`
- hits: `runtime_mutation, autonomous_execution`
  - L43: `            "runtime_mutation_enabled": False,`
  - L45: `            "autonomous_execution_expansion": False,`
### `claire\api\canonical_cockpit_surface_health.py`
- hits: `autonomous_execution`
  - L104: `            "autonomous_execution_expansion": False,`
### `claire\api\canonical_cockpit_surface_registry.py`
- hits: `autonomous_execution`
  - L140: `            "autonomous_execution_expansion": False,`
### `claire\api\cockpit_action_intent_contract.py`
- hits: `runtime_mutation, automatic_updates`
  - L55: `            "blocked_reason": "automatic_updates_blocked",`
  - L58: `            "intent_id": "execute_runtime_mutation",`
  - L64: `            "blocked_reason": "runtime_mutation_blocked",`
### `claire\api\cockpit_action_registry.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L27: `    triggers_autonomous_execution: bool`
  - L46: `            triggers_autonomous_execution=False,`
  - L58: `            triggers_autonomous_execution=False,`
  - L70: `            triggers_autonomous_execution=False,`
  - L82: `            triggers_autonomous_execution=False,`
### `claire\api\cockpit_diagnostics_drawer_payload.py`
- hits: `runtime_mutation`
  - L41: `        "allows_runtime_mutation": False,`
### `claire\api\cockpit_disabled_button_behavior.py`
- hits: `runtime_mutation, automatic_updates`
  - L12: `            "reason": "automatic_updates_blocked",`
  - L16: `            "button_id": "execute_runtime_mutation",`
  - L19: `            "reason": "runtime_mutation_blocked",`
### `claire\api\cockpit_dry_run_trigger_quarantine_view.py`
- hits: `automatic_updates, autonomous_execution`
  - L55: `        "autonomous_execution": "blocked",`
  - L56: `        "automatic_updates": "blocked",`
### `claire\api\cockpit_live_governance_banners.py`
- hits: `runtime_mutation, automatic_updates`
  - L27: `            "banner_id": "automatic_updates_blocked",`
  - L33: `            "banner_id": "runtime_mutation_blocked",`
### `claire\api\cockpit_manual_review_gate.py`
- hits: `automatic_updates, autonomous_execution`
  - L54: `        "autonomous_execution": "blocked",`
  - L55: `        "automatic_updates": "blocked",`
### `claire\api\cockpit_metadata_probe_trigger_contract.py`
- hits: `automatic_updates, autonomous_execution`
  - L42: `        "autonomous_execution": "blocked",`
  - L43: `        "automatic_updates": "blocked",`
### `claire\api\cockpit_monitoring_snapshot.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L28: `            "runtime_mutation_blocked": True,`
  - L29: `            "automatic_updates_blocked": True,`
  - L30: `            "autonomous_execution_blocked": True,`
### `claire\api\cockpit_operational_proof_routes.py`
- hits: `automatic_updates, autonomous_execution`
  - L71: `        "autonomous_execution_enabled": False,`
  - L72: `        "automatic_updates_enabled": False,`
### `claire\api\cockpit_operator_control_readiness.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L37: `            "runtime_mutation",`
  - L38: `            "automatic_updates",`
  - L39: `            "autonomous_execution",`
### `claire\api\cockpit_operator_next_actions.py`
- hits: `runtime_mutation, automatic_updates`
  - L41: `            "blocked_reason": "automatic_updates_blocked",`
  - L44: `            "action_id": "execute_runtime_mutation",`
  - L48: `            "blocked_reason": "runtime_mutation_blocked",`
### `claire\api\cockpit_shell_payload_assembler.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L53: `            "runtime_mutation": False,`
  - L54: `            "automatic_updates": False,`
  - L55: `            "autonomous_execution": False,`
### `claire\api\cockpit_state_consolidator.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L52: `            "runtime_mutation": False,`
  - L53: `            "automatic_updates": False,`
  - L54: `            "autonomous_execution": False,`
### `claire\api\cockpit_static_shell_manifest.py`
- hits: `runtime_mutation`
  - L29: `            "execute_runtime_mutation",`
### `claire\api\cockpit_validation_lanes.py`
- hits: `forward_motion, runtime_mutation, automatic_updates, autonomous_execution`
  - L9: `    "runtime_mutation": False,`
  - L10: `    "automatic_updates": False,`
  - L11: `    "autonomous_execution": False,`
  - L23: `    allowed_for_forward_motion: bool`
  - L35: `            allowed_for_forward_motion=True,`
### `claire\api\cockpit_visual_controls.py`
- hits: `forward_motion, runtime_mutation, automatic_updates, autonomous_execution`
  - L12: `    "runtime_mutation_blocked": True,`
  - L13: `    "automatic_updates_blocked": True,`
  - L14: `    "autonomous_execution_blocked": True,`
  - L90: `        "action_id": "execute_runtime_mutation",`
  - L98: `        "blocked_reason": "runtime_mutation_blocked",`
### `claire\api\cockpit_warning_banner_contracts.py`
- hits: `runtime_mutation, automatic_updates`
  - L9: `            "banner_id": "runtime_mutation_blocked",`
  - L11: `            "visible_when": "runtime_mutation_requested",`
  - L16: `            "banner_id": "automatic_updates_blocked",`
### `claire\api\continuous_browser_runtime_loop.py`
- hits: `runtime_mutation, autonomous_execution`
  - L46: `            "runtime_mutation_enabled": False,`
  - L53: `            "autonomous_execution_expansion": False,`
### `claire\api\continuous_governed_loop_contract.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L18: `        "automatic_updates_enabled": False,`
  - L31: `            "autonomous_runtime_mutation",`
  - L39: `        "autonomous_execution": "blocked",`
  - L40: `        "automatic_updates": "blocked",`
### `claire\api\continuous_runtime_presence.py`
- hits: `autonomous_execution`
  - L61: `            "autonomous_execution_expansion": False,`
### `claire\api\controlled_guarded_endpoint_registration_attempt.py`
- hits: `automatic_updates, autonomous_execution`
  - L47: `        "autonomous_execution": "blocked",`
  - L48: `        "automatic_updates": "blocked",`
### `claire\api\controlled_metadata_probe_executor.py`
- hits: `autonomous_execution`
  - L53: `        "autonomous_execution_performed": False,`
### `claire\api\controlled_read_only_provider_probe_gate.py`
- hits: `autonomous_execution`
  - L66: `        "autonomous_execution_performed": False,`
### `claire\api\dashboard_payload_bridge.py`
- hits: `automatic_updates`
  - L376: `    payload["automatic_updates_enabled"] = False`
  - L501: `    payload["automatic_updates_enabled"] = False`
### `claire\api\explicit_one_shot_metadata_probe_runner.py`
- hits: `autonomous_execution`
  - L69: `        "autonomous_execution_performed": False,`
### `claire\api\first_guarded_live_update_path_contract.py`
- hits: `automatic_updates, autonomous_execution`
  - L64: `        "automatic_updates": "blocked",`
  - L65: `        "autonomous_execution": "blocked",`
### `claire\api\first_metadata_probe_dry_run_simulator.py`
- hits: `automatic_updates, autonomous_execution`
  - L49: `        "autonomous_execution": "blocked",`
  - L50: `        "automatic_updates": "blocked",`
### `claire\api\first_metadata_probe_operator_readiness_checklist.py`
- hits: `automatic_updates, autonomous_execution`
  - L67: `        "autonomous_execution": "blocked",`
  - L68: `        "automatic_updates": "blocked",`
### `claire\api\governed_backend_truth_surfaces.py`
- hits: `automatic_updates, autonomous_execution`
  - L13: `    "automatic_updates": False,`
  - L14: `    "autonomous_execution": False,`
### `claire\api\governed_blocked_capability_matrix.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L9: `            "capability": "automatic_updates",`
  - L15: `            "capability": "runtime_mutation",`
  - L27: `            "capability": "autonomous_execution",`
### `claire\api\governed_cockpit_attachment_gate_s128_s134.py`
- hits: `forward_motion, automatic_updates, autonomous_execution`
  - L19: `    "automatic_updates_blocked": True,`
  - L20: `    "autonomous_execution_blocked": True,`
  - L134: `            "automatic_updates_blocked",`
  - L135: `            "autonomous_execution_blocked",`
  - L179: `        "forward_motion_allowed": ok,`
### `claire\api\governed_cockpit_consumption_contracts.py`
- hits: `runtime_mutation, automatic_updates, autonomous_execution`
  - L13: `    "automatic_updates": False,`
  - L14: `    "autonomous_execution": False,`
  - L163: `            failures.append(f"{panel.get('panel')}_runtime_mutation_not_false")`
### `claire\api\governed_cockpit_integration_plan_s113r1.py`
- hits: `automatic_updates, autonomous_execution`
  - L71: `            "automatic_updates_blocked": True,`
  - L72: `            "autonomous_execution_blocked": True,`
### `claire\api\governed_cockpit_payload_visibility_s149_s155.py`
- hits: `safe_to_continue, stop_go, GO, runtime_mutation, automatic_updates, autonomous_execution`
  - L10: `    "runtime_mutation_enabled": False,`
  - L11: `    "automatic_updates_enabled": False,`
  - L12: `    "autonomous_execution_enabled": False,`
  - L119: `        "stop_go": "GO",`
  - L121: `        "safe_to_continue": True,`

## JSON Report
`diagnostics\symptom_reports\claire_symptom_report_20260515_133836.json`
