from tools.active_runtime_check import main as runtime_check_main


def test_active_runtime_check_passes():
    assert runtime_check_main() == 0
