
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_operator_route_contracts import write_operator_route_contracts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S41R9-R12 operator route contracts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_route_contracts")
    args = parser.parse_args()

    result = write_operator_route_contracts(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
