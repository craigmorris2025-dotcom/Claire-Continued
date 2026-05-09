from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SecretScanFinding:
    path: str
    line_number: int
    pattern_name: str
    detail: str


class SecretScanner:
    """Scans project text files for accidental secret material before deployment."""

    DEFAULT_EXCLUDED_DIRS = {
        ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
        "node_modules", "dist", "build", ".mypy_cache", "backups",
    }
    DEFAULT_EXTENSIONS = {".py", ".json", ".toml", ".yaml", ".yml", ".env", ".txt", ".md", ".ini", ".cfg"}
    PATTERNS = {
        "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "private_key": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
        "generic_secret_assignment": re.compile(
            r"(?i)\b(secret|api[_-]?key|token|password)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
        "bearer_token": re.compile(r"(?i)\bbearer\s+[a-z0-9._\-]{20,}"),
    }

    def __init__(self, excluded_dirs: Iterable[str] | None = None, extensions: Iterable[str] | None = None) -> None:
        self.excluded_dirs = set(excluded_dirs or self.DEFAULT_EXCLUDED_DIRS)
        self.extensions = set(extensions or self.DEFAULT_EXTENSIONS)

    def scan_text(self, text: str, path: str = "<memory>") -> list[SecretScanFinding]:
        findings: list[SecretScanFinding] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") and "example" in stripped.lower():
                continue
            for name, pattern in self.PATTERNS.items():
                if pattern.search(line):
                    findings.append(SecretScanFinding(path, line_number, name, "possible secret material detected"))
        return findings

    def scan_project(self, project_root: Path) -> list[SecretScanFinding]:
        root = Path(project_root)
        findings: list[SecretScanFinding] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in self.excluded_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in self.extensions and path.name != ".env":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(self.scan_text(text, str(path.relative_to(root))))
        return findings
