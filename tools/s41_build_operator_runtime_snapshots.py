
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_operator_runtime_snapshots import write_operator_runtime_snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S41R1-R4 operator runtime snapshots.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_runtime_snapshots")
    args = parser.parse_args()

    result = write_operator_runtime_snapshots(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
