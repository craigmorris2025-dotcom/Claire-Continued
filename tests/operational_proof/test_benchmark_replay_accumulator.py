from claire.operational_proof.benchmark_replay_accumulator import BenchmarkReplayAccumulator

def test_replay_match_scores_exact():
    acc = BenchmarkReplayAccumulator()
    record = acc.build_replay_record("run1", "bench1", {"a": 1}, {"a": 1})
    assert acc.score_replay_match(record)["score"] == 1.0
