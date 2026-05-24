from __future__ import annotations

import json
from pathlib import Path

from runtime_core.api.governed_promotion_review_gate import seal_manual_promotion_candidate


def main() -> int:
    result = seal_manual_promotion_candidate(Path.cwd())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
