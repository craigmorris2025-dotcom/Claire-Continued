#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from claire.lifecycle.stage_registry import ClaireStageRegistry
from claire.lifecycle.threshold_provenance import ThresholdProvenance


def main() -> int:
    payload = {
        "stage_registry": ClaireStageRegistry().as_payload(),
        "threshold_provenance": ThresholdProvenance().as_payload(),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
