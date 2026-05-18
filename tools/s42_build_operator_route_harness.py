
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.operator_route_harness import write_s42_live_route_harness


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S42R21-R28 isolated operator route harness proof.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_route_harness")
    args = parser.parse_args()

    result = write_s42_live_route_harness(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
