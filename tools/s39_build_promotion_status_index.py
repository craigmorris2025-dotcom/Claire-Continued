from __future__ import annotations

import json
from pathlib import Path

from claire.api.governed_promotion_review_gate import build_promotion_status_index


def main() -> int:
    result = build_promotion_status_index(Path.cwd())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
