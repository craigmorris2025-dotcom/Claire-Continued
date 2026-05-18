from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from claire.app import create_app


class BaselineRunner:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1]

    def run(self) -> int:
        report_path = self.root / "reports" / "baseline_runner.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            app = create_app()
            client = TestClient(app)

            checks = {
                "/health": client.get("/health").status_code,
                "/openapi.json": client.get("/openapi.json").status_code,
                "/dashboard/payload/status": client.get("/dashboard/payload/status").status_code,
                "/runtime/continuous/status": client.get("/runtime/continuous/status").status_code,
            }

            report = {
                "runner": "BaselineRunner",
                "status": "success",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "checks": checks,
            }

            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            return 0

        except Exception as exc:
            report = {
                "runner": "BaselineRunner",
                "status": "failed",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "error": f"{exc.__class__.__name__}: {exc}",
            }
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            return 1


def main() -> int:
    return BaselineRunner().run()


if __name__ == "__main__":
    raise SystemExit(main())
