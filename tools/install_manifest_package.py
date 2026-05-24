#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from runtime_core.install_safety.simple_manifest_installer import install_manifest

def main() -> int:
    parser = argparse.ArgumentParser(description="Install Claire manifest-style generated installer")
    parser.add_argument("--installer", required=True)
    parser.add_argument("--install", action="store_true")
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()
    payload = install_manifest(PROJECT_ROOT, PROJECT_ROOT / args.installer, install=args.install, run_tests=args.run_tests)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("passed") or not args.install else 1

if __name__ == "__main__":
    raise SystemExit(main())
