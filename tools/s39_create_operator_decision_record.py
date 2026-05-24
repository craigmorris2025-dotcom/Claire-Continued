from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_promotion_review_gate import create_operator_decision_record


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an S39 operator decision record without mutating runtime truth.")
    parser.add_argument("--decision", choices=["approved_for_future_controlled_promotion", "rejected", "needs_revision"], default="needs_revision")
    parser.add_argument("--operator-ack", default="NO")
    parser.add_argument("--operator-id", default="operator")
    parser.add_argument("--rationale", default="")
    args = parser.parse_args()
    result = create_operator_decision_record(Path.cwd(), decision=args.decision, operator_ack=args.operator_ack, operator_id=args.operator_id, rationale=args.rationale)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
