
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_operator_route_plateau import write_s41_operator_route_plateau


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S41R13-R16 operator route plateau artifacts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_route_plateau")
    args = parser.parse_args()

    result = write_s41_operator_route_plateau(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
