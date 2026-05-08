from pathlib import Path

ROOT = Path.cwd()

def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")

write("src/claire/enterprise/install_environment_verification.py", r"""
from __future__ import annotations

import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


INSTALL_ENV_PATH = Path("data/enterprise/install_environment_verification.json")

REQUIRED_PATHS = [
    "src/claire",
    "tests",
    "data",
]

PROTECTED_SPINE_MODULES = [
    "claire.runtime.runtime_command_contracts",
    "claire.runtime.runtime_command_dispatcher",
    "claire.runtime.command_execution_guard",
    "claire.live.source_registry",
    "claire.memory.strategic_memory_registry",
]


def _module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def verify_install_environment() -> Dict[str, Any]:
    path_checks = [
        {
            "path": path,
            "exists": Path(path).exists(),
        }
        for path in REQUIRED_PATHS
    ]

    module_checks = [
        {
            "module": module,
            "available": _module_available(module),
        }
        for module in PROTECTED_SPINE_MODULES
    ]

    missing_paths = [c for c in path_checks if not c["exists"]]
    missing_modules = [c for c in module_checks if not c["available"]]

    report = {
        "version": "16.78",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready" if not missing_paths and not missing_modules else "partial_or_blocked",
        "python_version": sys.version,
        "platform": platform.platform(),
        "path_checks": path_checks,
        "module_checks": module_checks,
        "missing_path_count": len(missing_paths),
        "missing_module_count": len(missing_modules),
        "notes": [
            "This verification checks local environment readiness.",
            "Enterprise deployment still requires secrets review, security review, and deployment-specific configuration.",
        ],
    }

    INSTALL_ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_ENV_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
""")

print("v16.78 install + environment verification installed.")
