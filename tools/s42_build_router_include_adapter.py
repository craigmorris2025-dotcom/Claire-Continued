
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.operator_router_include_adapter import write_router_include_adapter_artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S42R13-R20 router include adapter artifacts.")
    parser.add_argument("--out", default="output/operator_router_include_adapter")
    args = parser.parse_args()

    result = write_router_include_adapter_artifacts(Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
