
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_operator_state_digest import write_s41_operator_state_digest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S41R5-R8 operator current-state digest artifacts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_state_digest")
    args = parser.parse_args()

    result = write_s41_operator_state_digest(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
