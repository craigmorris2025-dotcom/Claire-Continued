
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_core.api.governed_cockpit_consumption_contracts import write_cockpit_consumption_contracts


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S40R5-R8 cockpit consumption contracts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/cockpit_consumption_contracts")
    args = parser.parse_args()

    result = write_cockpit_consumption_contracts(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
