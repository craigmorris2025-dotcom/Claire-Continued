from __future__ import annotations

import json
from pathlib import Path

from runtime_core.api.governed_manual_promotion_candidates import build_manual_promotion_package


def main() -> int:
    result = build_manual_promotion_package(Path.cwd())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
