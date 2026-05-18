
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.s43_app_integration_probe import write_s43_app_integration_probe


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S43R1-R8 controlled app integration probe.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/s43_app_integration_probe")
    args = parser.parse_args()

    result = write_s43_app_integration_probe(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
