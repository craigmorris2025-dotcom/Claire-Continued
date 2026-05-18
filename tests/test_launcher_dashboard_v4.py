from __future__ import annotations

from pathlib import Path


def test_root_launcher_uses_safe_python_module_invocation_and_dashboard_v5():
    text = Path("LAUNCH_CLAIRE.bat").read_text(encoding="utf-8")

    assert "set \"CLAIRE_PYTHON=%CLAIRE_ROOT%.venv\\Scripts\\python.exe\"" in text
    assert " -B -m uvicorn main:app " in text
    assert "\"%CLAIRE_PYTHON%\" -B -m uvicorn" in text
    assert "python.exe on line 1" not in text
    assert "http://%CLAIRE_HOST%:%CLAIRE_PORT%/dashboard/v5" in text
    assert "/health" in text
    assert "start \"Claire Backend\" /D \"%CLAIRE_ROOT%\" cmd /k" in text
