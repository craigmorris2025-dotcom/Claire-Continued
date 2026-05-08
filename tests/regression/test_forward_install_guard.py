from tools.forward_install_guard import run_guard


def test_forward_install_guard_runs():
    payload = run_guard()
    assert "status" in payload
    assert payload["check_count"] >= 5


def test_forward_install_guard_has_required_checks():
    payload = run_guard()
    names = {check["name"] for check in payload["checks"]}
    assert "protected_paths" in names
    assert "nested_repo_pollution" in names
    assert "active_placeholder_tests" in names
    assert "syntax_fast" in names
    assert "protected_imports" in names
