
from __future__ import annotations

import argparse
import json
from pathlib import Path

from claire.api.governed_backend_truth_surfaces import write_backend_truth_surface_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build S40R1-R4 backend truth surface artifacts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="output/backend_truth_surfaces")
    args = parser.parse_args()

    result = write_backend_truth_surface_payload(Path(args.root), Path(args.out))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
