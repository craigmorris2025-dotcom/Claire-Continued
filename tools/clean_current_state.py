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

from runtime_core.install_safety.current_state_cleaner import clean_current_state

def main() -> int:
    parser = argparse.ArgumentParser(description="Clean Claire current test/install state")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    payload = clean_current_state(PROJECT_ROOT, install=args.install)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
