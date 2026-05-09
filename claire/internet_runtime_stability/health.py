from __future__ import annotations

from pathlib import Path
from typing import Dict, List


class InternetRuntimeHealthChecker:
    def __init__(self, project_root: Path | None = None) -> None:
        self.root = project_root or Path.cwd()

    def check(self) -> Dict[str, object]:
        required_paths = [
            "src/claire/internet_activation",
            "src/claire/internet_runtime_integration",
            "src/claire/persistent_internet_campaigns",
            "src/claire/governed_campaign_scheduler",
        ]

        data_paths = [
            "data/internet_activation",
            "data/persistent_internet_campaigns",
            "data/governed_campaign_scheduler",
        ]

        missing_required = [path for path in required_paths if not (self.root / path).exists()]
        missing_data = [path for path in data_paths if not (self.root / path).exists()]

        status = "healthy"
        if missing_required:
            status = "not_ready"
        elif missing_data:
            status = "degraded"

        return {
            "status": status,
            "missing_required_paths": missing_required,
            "missing_data_paths": missing_data,
            "checks": {
                "internet_activation_present": (self.root / "src/claire/internet_activation").exists(),
                "internet_runtime_integration_present": (self.root / "src/claire/internet_runtime_integration").exists(),
                "persistent_campaigns_present": (self.root / "src/claire/persistent_internet_campaigns").exists(),
                "scheduler_present": (self.root / "src/claire/governed_campaign_scheduler").exists(),
            },
        }
