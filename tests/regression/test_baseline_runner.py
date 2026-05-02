from tools.run_claire_baseline import BaselineRunner


def test_baseline_runner_checks_pass():
    runner = BaselineRunner()
    assert runner.run() == 0
