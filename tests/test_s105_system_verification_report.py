from __future__ import annotations

import json
from pathlib import Path

from tools.s105_system_verification_report import build_report, main

def test_s105_check_builds_whole_system_report():
    report = build_report()
    assert report["report_version"] == "v19.89.8-S105-CHECK"
    assert report["stop_gate"] == "S105-CHECK"
    assert report["sections"]["files"]["ok"] is True
    assert report["sections"]["imports"]["ok"] is True
    assert report["sections"]["fastapi_operator_routes"]["ok"] is True
    assert report["sections"]["demo_contracts"]["ok"] is True
    assert report["sections"]["governance_locks"]["ok"] is True

def test_s105_check_report_writes_json_file():
    exit_code = main()
    assert exit_code == 0
    path = Path("reports/s105_system_verification_report.json")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["ok"] is True
    assert payload["forward_motion_allowed"] is True
    assert payload["next_allowed_phase"] == "S106 canonical runtime spine map"
