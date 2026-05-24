from __future__ import annotations

import json

from runtime_core.api.governed_cockpit_stop_gate_s112r1 import write_cockpit_artifact_stop_gate_report

def main() -> int:
    result = write_cockpit_artifact_stop_gate_report()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
