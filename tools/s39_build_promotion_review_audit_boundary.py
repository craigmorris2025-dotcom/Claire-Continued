from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_promotion_review_audit_boundary import write_review_audit_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S39R5-R8 proposal review audit artifacts.")
    parser.add_argument("--proposal", required=True, help="Path to manual promotion proposal package JSON.")
    parser.add_argument("--out", default="output/manual_promotion_review_audit", help="Output directory.")
    parser.add_argument("--operator-ack", default="NO", choices=["YES", "NO"])
    parser.add_argument("--reviewer", default=None)
    parser.add_argument("--decision", default="pending")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    proposal_path = Path(args.proposal)
    if not proposal_path.exists():
        raise SystemExit(f"Proposal package not found: {proposal_path}")

    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    files = write_review_audit_artifacts(
        proposal,
        Path(args.out),
        operator_ack=args.operator_ack,
        reviewer=args.reviewer,
        decision=args.decision,
        notes=args.notes,
    )

    print(json.dumps({key: str(value) for key, value in files.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
