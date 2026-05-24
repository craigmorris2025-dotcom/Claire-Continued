from __future__ import annotations

from pathlib import Path
import importlib
import py_compile


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "runtime_core" / "api" / "dashboard_payload_bridge.py"


def test_s31r6_bridge_compiles():
    py_compile.compile(str(BRIDGE), doraise=True)


def test_s31r6_bridge_contains_single_handoff():
    text = BRIDGE.read_text(encoding="utf-8")
    assert text.count("Claire v19.89.8-S31R6 governed dashboard payload bridge handoff") == 1
    assert text.count("compose_governed_payload(payload)") == 1


def test_s31r6_reconciliation_module_composes_operational_keys():
    module = importlib.import_module("runtime_core.api.governed_payload_reconciliation")
    payload = module.compose_governed_payload({})
    assert "governed_payload_reconciliation" in payload
    assert "governed_operational_topology_continuity" in payload
    assert payload["governed_payload_reconciliation"]["authority"]["runtime_authority"] == "blocked"


def test_s31r6_no_app_factory_patch_required():
    app_file = ROOT / "runtime_core" / "app.py"
    assert app_file.exists()
    text = app_file.read_text(encoding="utf-8")
    assert "v19.89.8-S31R6" not in text
