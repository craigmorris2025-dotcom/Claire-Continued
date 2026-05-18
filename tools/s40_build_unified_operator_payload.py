
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_unified_operator_payload import write_unified_operator_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S40R9-R12 unified backend operator payload.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/unified_operator_payload")
    args = parser.parse_args()

    result = write_unified_operator_payload(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
