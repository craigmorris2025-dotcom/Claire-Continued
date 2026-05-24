
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_s39_promotion_plateau_index import build_s39_plateau_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S39R13-R16 promotion plateau index artifacts.")
    parser.add_argument("--readiness-ledger", default="output/manual_promotion_readiness_ledger/promotion_readiness_ledger.jsonl")
    parser.add_argument("--decision-ledger", default="output/manual_promotion_readiness_ledger/operator_decision_ledger.jsonl")
    parser.add_argument("--out", default="output/manual_promotion_plateau")
    args = parser.parse_args()

    result = build_s39_plateau_artifacts(Path(args.readiness_ledger), Path(args.decision_ledger), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
