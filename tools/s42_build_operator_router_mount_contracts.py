
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_operator_router_mount_contracts import write_operator_router_mount_contracts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S42R5-R12 operator router mount contracts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/operator_router_mount_contracts")
    args = parser.parse_args()

    result = write_operator_router_mount_contracts(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
