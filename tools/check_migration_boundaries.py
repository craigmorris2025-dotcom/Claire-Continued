from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_SUFFIXES = {
    ".bat",
    ".css",
    ".env",
    ".example",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".toml",
    ".ts",
    ".yaml",
    ".yml",
}

CODE_SUFFIXES = {
    ".bat",
    ".js",
    ".ps1",
    ".py",
    ".ts",
    ".yaml",
    ".yml",
}

EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "archive",
    "artifacts",
    "audit",
    "audits",
    "data",
    "diagnostics",
    "docs",
    "exports",
    "logs",
    "operations",
    "output",
    "reports",
    "runtime_reports",
}

EXCLUDED_FILES = {
    Path("claire/__init__.py"),
    Path("tools/check_migration_boundaries.py"),
}

PY_IMPORT_PATTERN = re.compile(r"^\s*(from\s+claire\b|import\s+claire\b)")
ENV_READ_PATTERNS = {
    "python legacy env read": re.compile(r"(os\.environ|getenv|os\.getenv)\([^)]*['\"]CLAIRE_[A-Z0-9_]+"),
    "javascript legacy env read": re.compile(r"(process\.env\.CLAIRE_[A-Z0-9_]+|import\.meta\.env\.CLAIRE_[A-Z0-9_]+)"),
    "shell legacy env assignment": re.compile(r"^\s*(\$env:CLAIRE_[A-Z0-9_]+|set\s+CLAIRE_[A-Z0-9_]+|export\s+CLAIRE_[A-Z0-9_]+)"),
    "config legacy env key": re.compile(r"^\s*CLAIRE_[A-Z0-9_]+\s*[:=]"),
}


def is_active_file(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel in EXCLUDED_FILES:
        return False
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name == ".env.example":
        return True
    return path.suffix in ACTIVE_SUFFIXES


def is_comment(line: str, suffix: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if suffix == ".py":
        return stripped.startswith("#")
    if suffix in {".js", ".ts", ".css"}:
        return stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*")
    if suffix in {".bat", ".ps1", ".yml", ".yaml", ".toml", ".env", ".example"}:
        return stripped.startswith("#") or stripped.lower().startswith("rem ")
    return False


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not is_active_file(path):
            continue
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if path.suffix == ".py" and PY_IMPORT_PATTERN.search(line):
                failures.append(f"{rel}:{line_number}: legacy claire import: {line.strip()}")
                continue
            if path.suffix not in CODE_SUFFIXES and path.name != ".env.example":
                continue
            if is_comment(line, path.suffix):
                continue
            for label, pattern in ENV_READ_PATTERNS.items():
                if pattern.search(line):
                    failures.append(f"{rel}:{line_number}: {label}: {line.strip()}")

    if failures:
        print("Migration boundary check failed:")
        print("\n".join(failures))
        return 1

    print("Migration boundary check passed: no active claire imports or CLAIRE_* env references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
