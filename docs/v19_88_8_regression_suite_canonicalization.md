# v19.88.8 Regression Suite Canonicalization

Purpose: stop obsolete regression tests from defining the current Claire Syntalion operational plateau.

Architecture preserved:
- `claire.app:create_app` is canonical.
- Backend owns truth.
- Cockpit owns presentation only.
- Runtime truth over UI assumptions.
- Fail-closed governance.
- No backend runtime shim restored.
- No uncontrolled browsing enabled.

Quarantined obsolete tests/files:
- tests\_quarantine_legacy_backend_imports\test_contract.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\_quarantine_legacy_backend_imports\test_contract.py | contains obsolete pattern 'from backend'
- tests\_quarantine_legacy_backend_imports\test_engines.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\_quarantine_legacy_backend_imports\test_engines.py | contains obsolete pattern 'from backend'
- tests\_quarantine_legacy_backend_imports\test_pipeline.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\_quarantine_legacy_backend_imports\test_pipeline.py | contains obsolete pattern 'from backend'
- tests\_quarantine_legacy_backend_imports\test_scoring.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\_quarantine_legacy_backend_imports\test_scoring.py | contains obsolete pattern 'from backend'
- tests\conftest.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\conftest.py | contains obsolete pattern 'from backend'
- tests\test_v17_54_persistent_workspace_operational_flow.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v17_54_persistent_workspace_operational_flow.py | contains obsolete pattern 'workspace_persistence.js'
- tests\test_v17_55_live_intelligence_feed_narrative_flow.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v17_55_live_intelligence_feed_narrative_flow.py | contains obsolete pattern 'workspace_persistence.js'
- tests\test_v19_66_cockpit_root_legacy_dashboard_freeze_marker.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v19_66_cockpit_root_legacy_dashboard_freeze_marker.py | contains obsolete pattern 'legacy_dashboard'
- tests\test_v19_68_shared_api_client_canonical_payload_adapter.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v19_68_shared_api_client_canonical_payload_adapter.py | contains obsolete pattern 'legacy_dashboard'
- tests\test_v19_75_cockpit_launcher_readiness_gate.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v19_75_cockpit_launcher_readiness_gate.py | contains obsolete pattern 'legacy_dashboard'
- tests\test_v19_88_7H_no_backend_imports_in_tests.py -> archive\quarantined\v19_88_8_obsolete_regression_tests\tests\test_v19_88_7H_no_backend_imports_in_tests.py | contains obsolete pattern 'backend.api'; contains obsolete pattern 'from backend'; contains obsolete pattern 'import backend'

Canonical tests installed:
- tests\test_api.py
- tests\test_v19_88_8_no_backend_dependency.py
- tests\test_v19_88_8_no_legacy_dashboard_asset_assertions.py
- tests\test_v19_88_8_operational_plateau_contract.py
