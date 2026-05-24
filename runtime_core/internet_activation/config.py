from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from runtime_core.config.env import env_int, env_true, getenv


def _bool_env(name: str, default: bool = False) -> bool:
    value = getenv(name)
    if not value:
        return default
    return env_true(name)


def _int_env(name: str, default: int) -> int:
    return env_int(name, default)


@dataclass
class InternetActivationConfig:
    root: Path = field(default_factory=lambda: Path.cwd())
    data_dir: Path = field(default_factory=lambda: Path("data") / "internet_activation")
    max_results: int = field(default_factory=lambda: _int_env("PLATFORM_INTERNET_MAX_RESULTS", 5))
    max_bytes: int = field(default_factory=lambda: _int_env("PLATFORM_INTERNET_MAX_BYTES", 750000))
    timeout_seconds: int = field(default_factory=lambda: _int_env("PLATFORM_INTERNET_TIMEOUT_SECONDS", 15))
    allow_unknown_domains: bool = field(default_factory=lambda: _bool_env("PLATFORM_INTERNET_ALLOW_UNKNOWN_DOMAINS", False))
    search_provider: str = field(default_factory=lambda: getenv("PLATFORM_SEARCH_PROVIDER").strip().lower())
    allowed_domains: List[str] = field(default_factory=lambda: [
        "sec.gov", "federalregister.gov", "congress.gov", "nist.gov", "nih.gov",
        "who.int", "oecd.org", "worldbank.org", "imf.org", "reuters.com",
        "apnews.com", "ftc.gov", "justice.gov", "treasury.gov", "fda.gov",
        "energy.gov", "whitehouse.gov", "europa.eu", "ec.europa.eu", "gov.uk",
        "nature.com", "science.org", "arxiv.org",
    ])
    blocked_domains: List[str] = field(default_factory=list)
    allowed_content_types: List[str] = field(default_factory=lambda: [
        "text/html", "text/plain", "application/json", "application/pdf", "application/xml", "text/xml",
    ])
    blocked_extensions: List[str] = field(default_factory=lambda: [
        ".exe", ".dll", ".bat", ".cmd", ".ps1", ".sh", ".msi", ".dmg", ".pkg",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso", ".apk", ".jar",
        ".py", ".js", ".vbs", ".scr", ".com",
    ])

    def resolved_data_dir(self) -> Path:
        path = self.root / self.data_dir if not self.data_dir.is_absolute() else self.data_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def provider_keys(self) -> Dict[str, str]:
        return {
            "tavily": os.getenv("TAVILY_API_KEY", ""),
            "brave": os.getenv("BRAVE_SEARCH_API_KEY", ""),
            "serpapi": os.getenv("SERPAPI_API_KEY", ""),
            "bing": os.getenv("BING_SEARCH_API_KEY", ""),
        }
