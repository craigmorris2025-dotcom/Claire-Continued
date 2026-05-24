"""
Claire update package downloader.

v5.48 bootstrap:
- Downloads approved packages to a local staging directory.
- Supports file paths, file:// URLs, http://, and https://.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import hashlib
import json
import shutil
import time


class PackageDownloader:
    """Download or stage a Claire update package."""

    def __init__(self, project_root: Path, allowed_sources_path: Path | None = None) -> None:
        self.project_root = project_root
        self.allowed_sources_path = allowed_sources_path or project_root / "data" / "update_sources" / "allowed_sources.json"
        self.stage_dir = project_root / "data" / "update_downloads"
        self.stage_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str) -> Dict[str, Any]:
        self._assert_allowed(url)
        parsed = urlparse(url)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        filename = Path(parsed.path).name or f"claire_update_{stamp}.zip"
        if not filename.lower().endswith(".zip"):
            filename = filename + ".zip"
        destination = self.stage_dir / f"{stamp}_{filename}"

        if parsed.scheme in {"http", "https"}:
            req = Request(url, headers={"User-Agent": "Claire-Updater/5.48"})
            with urlopen(req, timeout=30) as response:
                destination.write_bytes(response.read())
        elif parsed.scheme == "file":
            shutil.copy2(Path(parsed.path), destination)
        elif parsed.scheme == "":
            shutil.copy2(Path(url), destination)
        else:
            raise ValueError(f"Unsupported update URL scheme: {parsed.scheme}")

        return {
            "status": "success",
            "url": url,
            "package_path": str(destination),
            "size_bytes": destination.stat().st_size,
            "sha256": self.sha256_file(destination),
        }

    def _assert_allowed(self, url: str) -> None:
        policy = self._load_allowed_sources()
        parsed = urlparse(url)
        scheme = parsed.scheme or "file"
        if scheme not in set(policy.get("allowed_schemes", [])):
            raise ValueError(f"Update source scheme is not allowed: {scheme}")

        if scheme in {"http", "https"}:
            allowed_domains = set(policy.get("allowed_domains", []))
            host = (parsed.hostname or "").lower()
            if not host or (allowed_domains and host not in allowed_domains):
                raise ValueError(f"Update source domain is not allowlisted: {host}")
        elif scheme == "file":
            if not policy.get("allow_file_urls", True):
                raise ValueError("file:// update sources are disabled by policy.")

    def _load_allowed_sources(self) -> Dict[str, Any]:
        if not self.allowed_sources_path.exists():
            return {
                "allowed_schemes": ["file"],
                "allowed_domains": [],
                "allow_file_urls": True,
            }
        return json.loads(self.allowed_sources_path.read_text(encoding="utf-8"))

    def sha256_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()


__all__ = ["PackageDownloader"]
