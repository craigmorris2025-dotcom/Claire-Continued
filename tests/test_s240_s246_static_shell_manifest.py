from __future__ import annotations

from pathlib import Path

from runtime_core.api.cockpit_static_shell_manifest import get_static_shell_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_s240_s246_static_shell_manifest_lists_real_files_and_regions():
    payload = get_static_shell_manifest()

    assert payload["version"] == "v19.89.8-S240-S246"
    assert payload["unsafe_authority_enabled"] is False

    for rel_path in payload["shell_files"]:
        assert (ROOT / rel_path).exists(), rel_path

    assert "top_command_bar" in payload["render_regions"]
    assert "primary_runtime_panel" in payload["render_regions"]
    assert "operations_strip" in payload["render_regions"]
    assert "monitoring_column" in payload["render_regions"]
    assert "diagnostics_drawer" in payload["render_regions"]


def test_s240_s246_static_shell_manifest_uses_only_safe_fetch_endpoints():
    payload = get_static_shell_manifest()

    assert set(payload["safe_fetch_endpoints"]) == {
        "/dashboard/payload",
        "/dashboard/payload/status",
        "/health",
    }
    assert "execute_runtime_mutation" in payload["blocked_actions"]
    assert "run_autonomous_update" in payload["blocked_actions"]
