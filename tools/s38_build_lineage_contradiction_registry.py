from __future__ import annotations

import json
from pathlib import Path

from claire.api.governed_manual_promotion_candidates import build_lineage_contradiction_registry


def main() -> int:
    result = build_lineage_contradiction_registry(Path.cwd())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
