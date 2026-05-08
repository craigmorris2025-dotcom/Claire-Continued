# Claire Syntalion Installer
# v17.41 Claire Internet Activation Package
#
# Place this file in the Claire project root and run:
#     python install_v17_41_claire_internet_activation_package.py
#
# Then test:
#     python -m pytest tests/internet_activation -q

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
CLAIRE = ROOT / "src" / "claire"
LAYER = CLAIRE / "internet_activation"
TESTS = ROOT / "tests" / "internet_activation"
DATA = ROOT / "data" / "internet_activation"
DOCS = ROOT / "docs" / "internet_activation"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_env_example() -> None:
    env_example = ROOT / ".env.example"
    block = """
# Claire v17.41 Internet Activation
CLAIRE_SEARCH_PROVIDER=
TAVILY_API_KEY=
BRAVE_SEARCH_API_KEY=
SERPAPI_API_KEY=
BING_SEARCH_API_KEY=
CLAIRE_INTERNET_MAX_RESULTS=5
CLAIRE_INTERNET_MAX_BYTES=750000
CLAIRE_INTERNET_TIMEOUT_SECONDS=15
CLAIRE_INTERNET_ALLOW_UNKNOWN_DOMAINS=false
""".strip()
    existing = env_example.read_text(encoding="utf-8") if env_example.exists() else ""
    if "Claire v17.41 Internet Activation" not in existing:
        env_example.write_text(existing.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
        print(f"UPDATED {env_example.relative_to(ROOT)}")
    else:
        print(f"UNCHANGED {env_example.relative_to(ROOT)}")


def main() -> None:
    print("Installing Claire v17.41 Internet Activation Package...")

    write_file(LAYER / "__init__.py", '''
from .service import InternetResearchService
from .config import InternetActivationConfig
from .policy import InternetPolicyEngine
from .http_fetcher import GovernedHttpFetcher
from .search import SearchProviderRegistry
from .evidence import EvidenceExtractor
from .persistence import InternetResearchStore

__all__ = [
    "InternetResearchService",
    "InternetActivationConfig",
    "InternetPolicyEngine",
    "GovernedHttpFetcher",
    "SearchProviderRegistry",
    "EvidenceExtractor",
    "InternetResearchStore",
]
''')

    write_file(LAYER / "config.py", '''
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass
class InternetActivationConfig:
    root: Path = field(default_factory=lambda: Path.cwd())
    data_dir: Path = field(default_factory=lambda: Path("data") / "internet_activation")
    max_results: int = field(default_factory=lambda: _int_env("CLAIRE_INTERNET_MAX_RESULTS", 5))
    max_bytes: int = field(default_factory=lambda: _int_env("CLAIRE_INTERNET_MAX_BYTES", 750000))
    timeout_seconds: int = field(default_factory=lambda: _int_env("CLAIRE_INTERNET_TIMEOUT_SECONDS", 15))
    allow_unknown_domains: bool = field(default_factory=lambda: _bool_env("CLAIRE_INTERNET_ALLOW_UNKNOWN_DOMAINS", False))
    search_provider: str = field(default_factory=lambda: os.getenv("CLAIRE_SEARCH_PROVIDER", "").strip().lower())
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
''')

    write_file(LAYER / "models.py", '''
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class PolicyDecision:
    decision: str
    url: Optional[str] = None
    domain: Optional[str] = None
    reason: str = ""
    requires_review: bool = False
    content_allowed: bool = True
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    source: str = "search_provider"
    rank: int = 0
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class FetchResult:
    url: str
    status: str
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    text: str = ""
    binary_size: int = 0
    error: Optional[str] = None
    policy: Dict[str, Any] = field(default_factory=dict)
    fetched_at: str = field(default_factory=utc_now)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class EvidenceRecord:
    evidence_id: str
    run_id: str
    query: str
    source_url: str
    title: str
    claim: str
    summary: str
    source_domain: str
    source_reliability: float
    confidence: float
    supporting_terms: List[str] = field(default_factory=list)
    conflicting_terms: List[str] = field(default_factory=list)
    extracted_at: str = field(default_factory=utc_now)
    lineage: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)


@dataclass
class ResearchRun:
    run_id: str
    query: str
    status: str
    search_provider: str
    searched: bool = False
    fetched_count: int = 0
    evidence_count: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    def to_dict(self) -> Dict[str, Any]: return asdict(self)
''')

    write_file(LAYER / "policy.py", '''
from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .config import InternetActivationConfig
from .models import PolicyDecision


class InternetPolicyEngine:
    def __init__(self, config: InternetActivationConfig) -> None:
        self.config = config

    def domain_from_url(self, url: str) -> str:
        return urlparse(url).netloc.lower().replace("www.", "")

    def extension_from_url(self, url: str) -> str:
        return Path(urlparse(url).path).suffix.lower()

    def evaluate_url(self, url: str) -> PolicyDecision:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return PolicyDecision("blocked", url=url, reason="Only http and https URLs are allowed.", requires_review=True, content_allowed=False)
        domain = self.domain_from_url(url)
        if not domain:
            return PolicyDecision("blocked", url=url, reason="URL has no valid domain.", requires_review=True, content_allowed=False)
        ext = self.extension_from_url(url)
        if ext in self.config.blocked_extensions:
            return PolicyDecision("blocked", url=url, domain=domain, reason=f"Blocked file extension: {ext}", requires_review=True, content_allowed=False)
        if domain in set(self.config.blocked_domains):
            return PolicyDecision("blocked", url=url, domain=domain, reason="Domain is explicitly blocked.", requires_review=True, content_allowed=False)
        allowed = set(self.config.allowed_domains)
        if domain in allowed or any(domain.endswith("." + item) for item in allowed):
            return PolicyDecision("allowed", url=url, domain=domain, reason="Domain is allowlisted.")
        if self.config.allow_unknown_domains:
            return PolicyDecision("allowed_unknown", url=url, domain=domain, reason="Unknown domain allowed by config.")
        return PolicyDecision("review_required", url=url, domain=domain, reason="Unknown domain requires review before fetch.", requires_review=True, content_allowed=False)

    def evaluate_content_type(self, content_type: Optional[str]) -> PolicyDecision:
        if not content_type:
            return PolicyDecision("allowed", reason="No content type provided; enforcing byte and text limits.")
        base = content_type.split(";")[0].strip().lower()
        if base in set(self.config.allowed_content_types):
            return PolicyDecision("allowed", reason=f"Allowed content type: {base}")
        return PolicyDecision("blocked", reason=f"Blocked content type: {base}", requires_review=True, content_allowed=False)
''')

    write_file(LAYER / "http_fetcher.py", '''
from __future__ import annotations

import asyncio
from typing import Optional

import aiohttp

from .config import InternetActivationConfig
from .models import FetchResult
from .policy import InternetPolicyEngine


class GovernedHttpFetcher:
    def __init__(self, config: InternetActivationConfig, policy: Optional[InternetPolicyEngine] = None) -> None:
        self.config = config
        self.policy = policy or InternetPolicyEngine(config)

    async def fetch(self, url: str) -> FetchResult:
        policy_decision = self.policy.evaluate_url(url)
        if policy_decision.decision in {"blocked", "review_required"}:
            return FetchResult(url=url, status=policy_decision.decision, error=policy_decision.reason, policy=policy_decision.to_dict())

        timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        headers = {
            "User-Agent": "Claire-InternetActivation/17.41 (+governed research)",
            "Accept": "text/html,text/plain,application/json,application/pdf,application/xml,text/xml;q=0.9,*/*;q=0.2",
        }
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    content_type = response.headers.get("Content-Type")
                    content_policy = self.policy.evaluate_content_type(content_type)
                    if not content_policy.content_allowed:
                        return FetchResult(url=str(response.url), status="blocked_content_type", http_status=response.status, content_type=content_type, error=content_policy.reason, policy={"url_policy": policy_decision.to_dict(), "content_policy": content_policy.to_dict()})
                    raw = await response.content.read(self.config.max_bytes + 1)
                    truncated = len(raw) > self.config.max_bytes
                    raw = raw[: self.config.max_bytes]
                    return FetchResult(
                        url=str(response.url),
                        status="success" if response.status < 400 else "http_error",
                        http_status=response.status,
                        content_type=content_type,
                        text=self._decode(raw, content_type),
                        binary_size=len(raw),
                        error="Content truncated at max_bytes." if truncated else None,
                        policy={"url_policy": policy_decision.to_dict(), "content_policy": content_policy.to_dict(), "truncated": truncated},
                    )
        except asyncio.TimeoutError:
            return FetchResult(url=url, status="timeout", error=f"Fetch timed out after {self.config.timeout_seconds} seconds.", policy=policy_decision.to_dict())
        except Exception as exc:
            return FetchResult(url=url, status="fetch_error", error=str(exc), policy=policy_decision.to_dict())

    def _decode(self, raw: bytes, content_type: Optional[str]) -> str:
        if not raw:
            return ""
        if content_type and "application/pdf" in content_type.lower():
            return f"[PDF downloaded safely: {len(raw)} bytes. Text extraction requires optional PDF parser.]"
        return raw.decode("utf-8", errors="replace")
''')

    write_file(LAYER / "search.py", '''
from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlencode

import aiohttp

from .config import InternetActivationConfig
from .models import SearchResult


class SearchProviderError(RuntimeError):
    pass


class BaseSearchProvider:
    name = "base"
    def __init__(self, api_key: str, config: InternetActivationConfig) -> None:
        self.api_key = api_key
        self.config = config
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        raise NotImplementedError


class TavilySearchProvider(BaseSearchProvider):
    name = "tavily"
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        payload = {"api_key": self.api_key, "query": query, "search_depth": "basic", "max_results": max_results, "include_answer": False, "include_raw_content": False}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)) as session:
            async with session.post("https://api.tavily.com/search", json=payload) as response:
                data = await response.json(content_type=None)
                if response.status >= 400: raise SearchProviderError(str(data))
                return [SearchResult(str(i.get("title", "")), str(i.get("url", "")), str(i.get("content", "")), self.name, n) for n, i in enumerate(data.get("results", [])[:max_results], 1)]


class BraveSearchProvider(BaseSearchProvider):
    name = "brave"
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        url = "https://api.search.brave.com/res/v1/web/search?" + urlencode({"q": query, "count": max_results})
        headers = {"Accept": "application/json", "X-Subscription-Token": self.api_key}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds), headers=headers) as session:
            async with session.get(url) as response:
                data = await response.json(content_type=None)
                if response.status >= 400: raise SearchProviderError(str(data))
                items = data.get("web", {}).get("results", [])
                return [SearchResult(str(i.get("title", "")), str(i.get("url", "")), str(i.get("description", "")), self.name, n) for n, i in enumerate(items[:max_results], 1)]


class SerpApiSearchProvider(BaseSearchProvider):
    name = "serpapi"
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        url = "https://serpapi.com/search.json?" + urlencode({"q": query, "api_key": self.api_key, "num": max_results})
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)) as session:
            async with session.get(url) as response:
                data = await response.json(content_type=None)
                if response.status >= 400: raise SearchProviderError(str(data))
                return [SearchResult(str(i.get("title", "")), str(i.get("link", "")), str(i.get("snippet", "")), self.name, n) for n, i in enumerate(data.get("organic_results", [])[:max_results], 1)]


class BingSearchProvider(BaseSearchProvider):
    name = "bing"
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        url = "https://api.bing.microsoft.com/v7.0/search?" + urlencode({"q": query, "count": max_results})
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds), headers=headers) as session:
            async with session.get(url) as response:
                data = await response.json(content_type=None)
                if response.status >= 400: raise SearchProviderError(str(data))
                items = data.get("webPages", {}).get("value", [])
                return [SearchResult(str(i.get("name", "")), str(i.get("url", "")), str(i.get("snippet", "")), self.name, n) for n, i in enumerate(items[:max_results], 1)]


class SearchProviderRegistry:
    PROVIDERS = {"tavily": TavilySearchProvider, "brave": BraveSearchProvider, "serpapi": SerpApiSearchProvider, "bing": BingSearchProvider}
    def __init__(self, config: InternetActivationConfig) -> None:
        self.config = config
    def configured_provider_name(self) -> Optional[str]:
        keys = self.config.provider_keys(); requested = self.config.search_provider
        if requested and requested in self.PROVIDERS and keys.get(requested): return requested
        for name in ("tavily", "brave", "serpapi", "bing"):
            if keys.get(name): return name
        return None
    def provider(self) -> Optional[BaseSearchProvider]:
        name = self.configured_provider_name()
        if not name: return None
        return self.PROVIDERS[name](self.config.provider_keys()[name], self.config)
    async def search(self, query: str, max_results: int) -> List[SearchResult]:
        provider = self.provider()
        if provider is None: return []
        return await provider.search(query, max_results)
''')

    write_file(LAYER / "normalizer.py", '''
from __future__ import annotations

import json, re
from html.parser import HTMLParser
from typing import List, Tuple


class _HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.parts=[]; self.title_parts=[]; self.in_title=False; self.skip_depth=0
    def handle_starttag(self, tag, attrs):
        if tag.lower()=="title": self.in_title=True
        if tag.lower() in {"script","style","noscript"}: self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag.lower()=="title": self.in_title=False
        if tag.lower() in {"script","style","noscript"} and self.skip_depth: self.skip_depth -= 1
    def handle_data(self, data):
        if self.skip_depth: return
        clean=" ".join(data.split())
        if not clean: return
        if self.in_title: self.title_parts.append(clean)
        self.parts.append(clean)


class ContentNormalizer:
    def normalize(self, text: str, content_type: str | None = None) -> Tuple[str, str, List[str]]:
        if not text: return "Untitled", "", []
        base=(content_type or "").split(";")[0].strip().lower()
        if base == "application/json":
            try: text=json.dumps(json.loads(text), ensure_ascii=False, indent=2)
            except Exception: pass
            title="JSON source"
        elif "html" in base or "<html" in text.lower():
            parser=_HTMLTextParser(); parser.feed(text); title=" ".join(parser.title_parts).strip() or "HTML source"; text=" ".join(parser.parts)
        else:
            clean=" ".join(text.split()); title=clean[:90]+("..." if len(clean)>90 else "")
        normalized=" ".join(text.split())
        return title, normalized, self.terms(normalized)
    def terms(self, text: str) -> List[str]:
        words=re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
        stop={"that","this","with","from","have","will","were","been","their","there","which","about","would","could","should","https","http","html","page","more","also"}
        counts={}
        for w in words:
            if w not in stop: counts[w]=counts.get(w,0)+1
        return [w for w,_ in sorted(counts.items(), key=lambda x:x[1], reverse=True)[:20]]
''')

    write_file(LAYER / "reliability.py", '''
from __future__ import annotations


class SourceReliabilityScorer:
    HIGH = {"sec.gov":0.96,"federalregister.gov":0.94,"congress.gov":0.93,"nist.gov":0.93,"nih.gov":0.92,"who.int":0.90,"oecd.org":0.88,"worldbank.org":0.88,"imf.org":0.88,"ftc.gov":0.90,"justice.gov":0.90,"treasury.gov":0.90,"fda.gov":0.90,"energy.gov":0.88,"europa.eu":0.88,"ec.europa.eu":0.88,"gov.uk":0.88,"reuters.com":0.82,"apnews.com":0.82,"nature.com":0.82,"science.org":0.82,"arxiv.org":0.72}
    def score(self, domain: str, content_length: int = 0, search_rank: int = 0) -> float:
        base=self.HIGH.get(domain,0.55)
        if content_length < 200: base -= 0.08
        elif content_length > 2000: base += 0.03
        if search_rank: base += max(0.0, 0.04 - (search_rank * 0.005))
        return round(max(0.05, min(1.0, base)), 4)
''')

    write_file(LAYER / "evidence.py", '''
from __future__ import annotations

import hashlib
from typing import List
from urllib.parse import urlparse

from .models import EvidenceRecord, FetchResult, SearchResult
from .normalizer import ContentNormalizer
from .reliability import SourceReliabilityScorer


class EvidenceExtractor:
    def __init__(self) -> None:
        self.normalizer=ContentNormalizer(); self.reliability=SourceReliabilityScorer()
    def extract(self, run_id: str, query: str, fetch: FetchResult, search_result: SearchResult | None = None) -> List[EvidenceRecord]:
        if fetch.status != "success": return []
        title,text,terms=self.normalizer.normalize(fetch.text, fetch.content_type)
        if not text: return []
        domain=urlparse(fetch.url).netloc.lower().replace("www.","")
        rank=search_result.rank if search_result else 0
        reliability=self.reliability.score(domain, len(text), rank)
        claim=self._best_claim(text, query)
        summary=text[:700]+("..." if len(text)>700 else "")
        confidence=round(max(0.0, min(1.0, reliability*0.75 + self._term_overlap(query, terms)*0.25)),4)
        evidence_id="ev_"+hashlib.sha256(f"{run_id}|{fetch.url}|{claim}".encode()).hexdigest()[:16]
        return [EvidenceRecord(evidence_id, run_id, query, fetch.url, title or "Untitled source", claim, summary, domain, reliability, confidence, terms[:12], [], lineage={"http_status":fetch.http_status,"content_type":fetch.content_type,"search_source":search_result.source if search_result else "direct_url","search_rank":rank,"fetch_policy":fetch.policy,"binary_size":fetch.binary_size})]
    def _best_claim(self, text: str, query: str) -> str:
        sentences=[s.strip() for s in text.replace("\n"," ").split(".") if len(s.strip())>40]
        q={t.lower() for t in query.split() if len(t)>3}
        if not sentences: return text[:300]+("..." if len(text)>300 else "")
        best=sorted(sentences, key=lambda s: sum(1 for t in q if t in s.lower()), reverse=True)[0]
        return best[:500]+("..." if len(best)>500 else "")
    def _term_overlap(self, query: str, terms: List[str]) -> float:
        q={t.lower().strip(".,:;!?") for t in query.split() if len(t)>3}; t=set(terms)
        return 0.0 if not q else len(q & t)/len(q)
''')

    write_file(LAYER / "persistence.py", '''
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .config import InternetActivationConfig
from .models import EvidenceRecord, ResearchRun, utc_now


class InternetResearchStore:
    def __init__(self, config: InternetActivationConfig) -> None:
        self.config=config; self.root=config.resolved_data_dir()
        self.evidence_dir=self.root/"evidence"; self.runs_dir=self.root/"runs"; self.audit_dir=self.root/"audit"; self.cache_dir=self.root/"cache"
        for p in [self.evidence_dir,self.runs_dir,self.audit_dir,self.cache_dir]: p.mkdir(parents=True, exist_ok=True)
    def save_evidence(self, record: EvidenceRecord) -> Path:
        path=self.evidence_dir/f"{record.evidence_id}.json"; path.write_text(json.dumps(record.to_dict(), indent=2, sort_keys=True), encoding="utf-8"); return path
    def save_run(self, run: ResearchRun, output: Dict[str, Any]) -> Path:
        path=self.runs_dir/f"{run.run_id}.json"; path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8"); return path
    def audit(self, event_type: str, payload: Dict[str, Any]) -> Path:
        safe="".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in event_type)
        path=self.audit_dir/f"{utc_now().replace(':','').replace('.','_')}_{safe}.json"
        path.write_text(json.dumps({"event_type":event_type,"created_at":utc_now(),"payload":payload}, indent=2, sort_keys=True), encoding="utf-8"); return path
    def get_evidence(self, evidence_id: str) -> Dict[str, Any] | None:
        path=self.evidence_dir/f"{evidence_id}.json"
        return None if not path.exists() else json.loads(path.read_text(encoding="utf-8"))
    def list_evidence(self, limit: int = 50) -> List[Dict[str, Any]]:
        out=[]
        for path in sorted(self.evidence_dir.glob("*.json"), key=lambda p:p.stat().st_mtime, reverse=True)[:limit]:
            try: out.append(json.loads(path.read_text(encoding="utf-8")))
            except Exception: pass
        return out
''')

    write_file(LAYER / "service.py", '''
from __future__ import annotations

import asyncio, hashlib
from typing import Any, Dict, List, Optional

from .config import InternetActivationConfig
from .evidence import EvidenceExtractor
from .http_fetcher import GovernedHttpFetcher
from .models import ResearchRun, SearchResult
from .persistence import InternetResearchStore
from .search import SearchProviderError, SearchProviderRegistry


class InternetResearchService:
    def __init__(self, config: Optional[InternetActivationConfig] = None) -> None:
        self.config=config or InternetActivationConfig(); self.fetcher=GovernedHttpFetcher(self.config); self.search_registry=SearchProviderRegistry(self.config); self.extractor=EvidenceExtractor(); self.store=InternetResearchStore(self.config)

    async def research(self, query: str, urls: Optional[List[str]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        query=query.strip()
        if not query: raise ValueError("query is required")
        max_results=max(1, min(max_results or self.config.max_results, self.config.max_results))
        provider_name=self.search_registry.configured_provider_name() or "none"
        run_id="internet_run_"+hashlib.sha256(f"{query}|{provider_name}|{urls}".encode()).hexdigest()[:16]
        run=ResearchRun(run_id, query, "running", provider_name)
        warnings=[]; errors=[]; search_results=[]
        if urls:
            search_results=[SearchResult("Direct URL", url, "", "direct_url", idx) for idx,url in enumerate(urls[:max_results],1)]
        else:
            provider=self.search_registry.provider()
            if provider is None:
                run.status="not_configured"; warnings.append("No search provider configured. Add a supported API key to .env or pass explicit URLs.")
            else:
                try: search_results=await self.search_registry.search(query, max_results); run.searched=True
                except SearchProviderError as exc: errors.append(str(exc))
                except Exception as exc: errors.append(f"Search failed: {exc}")
        fetch_outputs=[]; evidence_outputs=[]
        for result in search_results[:max_results]:
            if not result.url: continue
            fetch=await self.fetcher.fetch(result.url); fetch_outputs.append(fetch.to_dict())
            if fetch.status != "success":
                if fetch.error: warnings.append(f"{fetch.url}: {fetch.status} - {fetch.error}")
                continue
            for record in self.extractor.extract(run_id, query, fetch, result):
                self.store.save_evidence(record); run.evidence_ids.append(record.evidence_id); evidence_outputs.append(record.to_dict())
        run.fetched_count=len(fetch_outputs); run.evidence_count=len(evidence_outputs); run.warnings=warnings; run.errors=errors
        run.status="completed" if evidence_outputs else ("completed_no_evidence" if not errors else "failed")
        if not search_results and not errors and warnings: run.status="not_configured"
        output={"layer":"internet_activation","version":"v17.41","run":run.to_dict(),"search_results":[i.to_dict() for i in search_results],"fetch_results":fetch_outputs,"evidence":evidence_outputs,"governance":{"allow_unknown_domains":self.config.allow_unknown_domains,"max_results":self.config.max_results,"max_bytes":self.config.max_bytes,"timeout_seconds":self.config.timeout_seconds,"blocked_extensions":self.config.blocked_extensions,"allowed_content_types":self.config.allowed_content_types}}
        self.store.save_run(run, output); self.store.audit("internet_research_run", {"run_id":run_id,"query":query,"status":run.status,"evidence_count":run.evidence_count,"warnings":warnings,"errors":errors})
        return output

    def research_sync(self, query: str, urls: Optional[List[str]] = None, max_results: Optional[int] = None) -> Dict[str, Any]:
        return asyncio.run(self.research(query, urls, max_results))
    def get_evidence(self, evidence_id: str) -> Dict[str, Any] | None: return self.store.get_evidence(evidence_id)
    def list_evidence(self, limit: int = 50) -> List[Dict[str, Any]]: return self.store.list_evidence(limit)
''')

    write_file(LAYER / "api_routes.py", '''
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .service import InternetResearchService

router = APIRouter(prefix="/research", tags=["Internet Research"])


class InternetResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    urls: Optional[List[str]] = None
    max_results: Optional[int] = Field(default=None, ge=1, le=20)


@router.post("/internet")
async def research_internet(request: InternetResearchRequest):
    service = InternetResearchService()
    try:
        return await service.research(request.query, request.urls, request.max_results)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/internet/evidence")
def list_internet_evidence(limit: int = 50):
    return {"evidence": InternetResearchService().list_evidence(limit)}


@router.get("/internet/evidence/{evidence_id}")
def get_internet_evidence(evidence_id: str):
    record = InternetResearchService().get_evidence(evidence_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return record
''')

    write_file(TESTS / "test_internet_activation.py", '''
from pathlib import Path
import pytest
from claire.internet_activation.config import InternetActivationConfig
from claire.internet_activation.models import FetchResult
from claire.internet_activation.policy import InternetPolicyEngine
from claire.internet_activation.service import InternetResearchService


def test_policy_blocks_executable_extension(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://www.sec.gov/file.exe")
    assert decision.decision == "blocked"


def test_policy_allows_allowlisted_domain(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://www.sec.gov/newsroom")
    assert decision.decision == "allowed"


def test_policy_unknown_domain_requires_review_by_default(tmp_path: Path):
    decision=InternetPolicyEngine(InternetActivationConfig(root=tmp_path)).evaluate_url("https://example.com/report")
    assert decision.decision == "review_required"


@pytest.mark.asyncio
async def test_research_with_mocked_fetch_saves_evidence(tmp_path: Path, monkeypatch):
    service=InternetResearchService(InternetActivationConfig(root=tmp_path, data_dir=Path("data")/"internet_activation"))
    async def fake_fetch(url: str):
        return FetchResult(url=url,status="success",http_status=200,content_type="text/html",text="<html><title>SEC AI Rule</title><body>Artificial intelligence disclosure rules and governance requirements are increasing for public companies.</body></html>",binary_size=150,policy={"url_policy":{"decision":"allowed"}})
    monkeypatch.setattr(service.fetcher, "fetch", fake_fetch)
    result=await service.research("artificial intelligence disclosure rules", urls=["https://www.sec.gov/newsroom"], max_results=1)
    assert result["run"]["status"] == "completed"
    assert result["run"]["evidence_count"] == 1
    assert service.get_evidence(result["evidence"][0]["evidence_id"]) is not None


@pytest.mark.asyncio
async def test_search_not_configured_without_urls_returns_not_configured(tmp_path: Path):
    result=await InternetResearchService(InternetActivationConfig(root=tmp_path)).research("test query", urls=None, max_results=1)
    assert result["run"]["status"] == "not_configured"
    assert result["run"]["evidence_count"] == 0


@pytest.mark.asyncio
async def test_review_required_url_does_not_fetch_evidence(tmp_path: Path):
    result=await InternetResearchService(InternetActivationConfig(root=tmp_path)).research("unknown domain", urls=["https://unknown-domain-example.invalid/page"], max_results=1)
    assert result["run"]["evidence_count"] == 0
    assert result["fetch_results"][0]["status"] == "review_required"
''')

    write_file(TESTS / "test_internet_activation_api.py", '''
from fastapi import FastAPI
from fastapi.testclient import TestClient
from claire.internet_activation import api_routes
from claire.internet_activation.service import InternetResearchService


def test_api_route_research_with_mocked_service(monkeypatch):
    app=FastAPI(); app.include_router(api_routes.router)
    async def fake_research(self, query, urls=None, max_results=None):
        return {"layer":"internet_activation","version":"v17.41","run":{"run_id":"test","query":query,"status":"completed","evidence_count":1,"evidence_ids":["ev_test"]},"evidence":[{"evidence_id":"ev_test","claim":"test claim"}]}
    monkeypatch.setattr(InternetResearchService, "research", fake_research)
    response=TestClient(app).post("/research/internet", json={"query":"ai policy","urls":["https://www.sec.gov/newsroom"],"max_results":1})
    assert response.status_code == 200
    assert response.json()["run"]["status"] == "completed"
''')

    write_file(DOCS / "v17_41_claire_internet_activation_package.md", '''
# Claire v17.41 — Internet Activation Package

This package activates a real governed internet research core for Claire.

## Provides

- Real asynchronous HTTP fetching through `aiohttp`
- Search provider support through `.env`: Tavily, Brave Search, SerpAPI, Bing Search
- Source governance: allowlist, deny list, review-required unknown domains, blocked unsafe file extensions, MIME filtering
- Evidence extraction: normalized text, title, claim, summary, source URL/domain, reliability, confidence, lineage
- Persistence: `data/internet_activation/evidence`, `runs`, `audit`, `cache`
- FastAPI routes: `POST /research/internet`, `GET /research/internet/evidence`, `GET /research/internet/evidence/{evidence_id}`

## Route Wiring

```python
from claire.internet_activation.api_routes import router as internet_research_router
app.include_router(internet_research_router)
```

## Search Provider Setup

Configure one provider in `.env`, for example:

```env
CLAIRE_SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_key_here
```

Without a provider key, Claire can still fetch explicit approved URLs passed to `/research/internet`.

## Governance Boundary

No hidden browsing, no executable downloads, no unapproved unknown domains, no credential use except configured search API keys, no self-modifying code, and no autonomous external action.
''')

    write_json(DATA / "internet_activation_manifest.json", {
        "installed_at": utc_now(),
        "layer": "internet_activation",
        "version": "v17.41",
        "status": "installed",
        "implementation_type": "real_local_internet_activation_core",
        "capabilities": ["real_aiohttp_fetch", "tavily_search", "brave_search", "serpapi_search", "bing_search", "source_policy", "safe_download_filter", "content_normalization", "evidence_extraction", "evidence_persistence", "audit_logging", "fastapi_routes", "mocked_network_tests"],
        "governance_boundary": "no_hidden_browsing_no_executable_downloads_no_unapproved_unknown_domains",
        "not_claimed": ["cloud_deployment", "kubernetes", "distributed_queue_broker", "browser_automation", "autonomous_unrestricted_crawling", "private_authenticated_browsing"]
    })

    append_env_example()
    print("\nINSTALL COMPLETE: Claire v17.41 Internet Activation Package")
    print("Run tests with:")
    print("    python -m pytest tests/internet_activation -q")
    print("Wire routes:")
    print("    from claire.internet_activation.api_routes import router as internet_research_router")
    print("    app.include_router(internet_research_router)")


if __name__ == "__main__":
    main()
