
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_promotion_readiness_ledger import build_promotion_readiness_ledgers


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S39R9-R12 non-authoritative promotion readiness ledgers.")
    parser.add_argument("--audit-boundary-dir", default="output/manual_promotion_review_audit")
    parser.add_argument("--out", default="output/manual_promotion_readiness_ledger")
    parser.add_argument("--reviewer", default=None)
    parser.add_argument("--decision", default="pending")
    parser.add_argument("--operator-ack", default="NO", choices=["YES", "NO"])
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    result = build_promotion_readiness_ledgers(
        Path(args.audit_boundary_dir),
        Path(args.out),
        reviewer=args.reviewer,
        decision=args.decision,
        operator_ack=args.operator_ack,
        notes=args.notes,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
