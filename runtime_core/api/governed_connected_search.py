from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from hashlib import sha256
from html import escape as html_escape
from html.parser import HTMLParser
from ipaddress import ip_address
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from runtime_core.config.env import env_true, getenv
from runtime_core.governance.governed_search_result_quarantine import build_quarantine_store
from runtime_core.governance.governed_source_registry import classify_source


router = APIRouter(tags=["Governed Connected Search"])

VERSION = "v19.89.8-connected-search-metadata-v1"
PROVIDER_KEYS = {
    "brave": "BRAVE_SEARCH_API_KEY",
    "bing": "BING_SEARCH_API_KEY",
    "duckduckgo": "",
    "searchgov": "SEARCHGOV_ACCESS_KEY",
    "serpapi": "SERPAPI_API_KEY",
    "tavily": "TAVILY_API_KEY",
}
RECOMMENDED_PROVIDER_STACK = ["brave", "searchgov", "duckduckgo"]
FALLBACK_ONLY_PROVIDERS = {"duckduckgo"}
DEFAULT_MAX_RESULTS = 6
PROMOTION_CONFIRM_TEXT = "PROMOTE_METADATA_TO_EVIDENCE"
MAX_BROWSER_RENDER_BYTES = 1_500_000
SECRET_ENV_NAMES = {
    "BING_SEARCH_API_KEY",
    "BRAVE_SEARCH_API_KEY",
    "PLATFORM_SEARCH_PROVIDER_API_KEY",
    "SEARCHGOV_ACCESS_KEY",
    "SEARCHGOV_AFFILIATE",
    "SERPAPI_API_KEY",
    "TAVILY_API_KEY",
}


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "main.py").exists() or (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def redact_secrets(value: Any) -> str:
    text = str(value)
    for name in SECRET_ENV_NAMES:
        secret = os.environ.get(name, "")
        if secret and len(secret) >= 4:
            text = text.replace(secret, "[redacted]")
    return text


def provider_gate_config() -> dict[str, Any]:
    path = project_root() / "data" / "internet_provider" / "provider_configuration_gate.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def configured_provider_stack(config: dict[str, Any]) -> list[str]:
    env_stack = getenv("PLATFORM_SEARCH_PROVIDER_STACK")
    if env_stack.strip():
        candidates = [item.strip().lower() for item in env_stack.split(",")]
    else:
        environment = config.get("environment", {}) if isinstance(config.get("environment"), dict) else {}
        configured = environment.get("provider_stack") or config.get("provider_stack") or []
        if isinstance(configured, str):
            candidates = [item.strip().lower() for item in configured.split(",")]
        elif isinstance(configured, list):
            candidates = [str(item).strip().lower() for item in configured]
        else:
            candidates = []
    stack = [item for item in candidates if item in PROVIDER_KEYS]
    provider = getenv("PLATFORM_SEARCH_PROVIDER").strip().lower()
    if provider in PROVIDER_KEYS and provider not in stack:
        stack.insert(0, provider)
    return stack


def provider_state() -> dict[str, Any]:
    config = provider_gate_config()
    environment = config.get("environment", {}) if isinstance(config.get("environment"), dict) else {}
    governance = config.get("governance", {}) if isinstance(config.get("governance"), dict) else {}
    provider = getenv("PLATFORM_SEARCH_PROVIDER").strip().lower() or str(environment.get("selected_provider") or "").strip().lower()
    if provider == "provider_stack":
        provider = ""
    stack = configured_provider_stack(config)
    if not provider and stack:
        provider = stack[0]
    key_name = PROVIDER_KEYS.get(provider, "")
    key_present = bool(key_name == "" and provider in PROVIDER_KEYS) or bool(key_name and os.environ.get(key_name))
    if provider == "searchgov":
        key_present = bool(
            os.environ.get("SEARCHGOV_ACCESS_KEY")
            and os.environ.get("SEARCHGOV_AFFILIATE")
        ) or bool(
            environment.get("searchgov_access_key_present")
            and environment.get("searchgov_affiliate_present")
        )
        key_name = "SEARCHGOV_ACCESS_KEY"
    allow_real = env_true("PLATFORM_ALLOW_REAL_SEARCH_PROVIDER") or bool(
        governance.get("governed_research_execution_enabled") or governance.get("normal_web_search_execution_enabled")
    )
    fallback_allowed = env_true("PLATFORM_ALLOW_DUCKDUCKGO_FALLBACK") or bool(
        governance.get("duckduckgo_fallback_enabled") or environment.get("duckduckgo_fallback_enabled")
    )
    stack_states = []
    for item in stack:
        item_key = PROVIDER_KEYS.get(item, "")
        item_is_fallback = item in FALLBACK_ONLY_PROVIDERS
        item_key_present = bool(item_key == "" and item in PROVIDER_KEYS and fallback_allowed) or bool(item_key and os.environ.get(item_key))
        if item == "searchgov":
            item_key_present = bool(
                os.environ.get("SEARCHGOV_ACCESS_KEY")
                and os.environ.get("SEARCHGOV_AFFILIATE")
            ) or bool(
                environment.get("searchgov_access_key_present")
                and environment.get("searchgov_affiliate_present")
            )
        execution_allowed = bool(item in PROVIDER_KEYS and item_key_present and allow_real)
        if item_is_fallback and not fallback_allowed:
            execution_allowed = False
        stack_states.append(
            {
                "provider": item,
                "required_key_name": item_key,
                "required_key_present": item_key_present,
                "execution_allowed": execution_allowed,
                "fallback_only": item_is_fallback,
                "fallback_allowed": fallback_allowed if item_is_fallback else None,
                "research_grade": not item_is_fallback,
            }
        )
    provider_is_fallback = provider in FALLBACK_ONLY_PROVIDERS
    if provider_is_fallback and not fallback_allowed:
        key_present = False
    return {
        "provider": provider or "none",
        "provider_known": provider in PROVIDER_KEYS,
        "required_key_name": key_name,
        "required_key_present": key_present,
        "real_provider_gate_enabled": allow_real,
        "execution_allowed": bool(provider in PROVIDER_KEYS and key_present and allow_real and (not provider_is_fallback or fallback_allowed)),
        "provider_stack": stack,
        "provider_stack_states": stack_states,
        "recommended_stack": RECOMMENDED_PROVIDER_STACK,
        "supported_providers": sorted(PROVIDER_KEYS),
        "fallback_only_providers": sorted(FALLBACK_ONLY_PROVIDERS),
        "duckduckgo_fallback_allowed": fallback_allowed,
        "research_grade_provider_required": True,
    }


def authority(network_performed: bool = False) -> dict[str, Any]:
    return {
        "provider_execution_performed": network_performed,
        "network_request_performed": network_performed,
        "metadata_only": True,
        "body_read_performed": False,
        "body_read_allowed": False,
        "browser_execution_performed": False,
        "autonomous_crawling_performed": False,
        "runtime_truth_mutation": False,
        "runtime_truth_write": "blocked",
        "automatic_update_performed": False,
        "manual_promotion_required": True,
        "quarantine_required": True,
    }


def search_lane_config() -> dict[str, Any]:
    state = provider_state()
    stack_execution_allowed = state["execution_allowed"] or any(
        item.get("execution_allowed") for item in state.get("provider_stack_states", [])
    )
    return {
        "version": VERSION,
        "status": "ready",
        "lanes": {
            "research_intake": {
                "label": "Research Intake",
                "trigger": "cockpit_search_enter_or_search_button",
                "endpoint": "/api/search/provider/query",
                "provider_execution_allowed": stack_execution_allowed,
                "metadata_only": True,
                "quarantine_required": True,
                "manual_promotion_required": True,
                "feeds_pipeline": True,
                "description": "Turns the search term into a governed R&D seed, provider metadata query, quarantine record, command plan, and optional promoted-evidence hybrid result.",
            },
            "government_public_sector": {
                "label": "Government / Public Sector",
                "trigger": "gov_source_lane_when_provider_stack_enabled",
                "endpoint": "/api/search/provider/query",
                "provider": "searchgov",
                "provider_execution_allowed": any(
                    item.get("provider") == "searchgov" and item.get("execution_allowed")
                    for item in state.get("provider_stack_states", [])
                ),
                "metadata_only": True,
                "quarantine_required": True,
                "manual_promotion_required": True,
                "feeds_pipeline": True,
                "description": "Uses Search.gov/GSA when configured to collect federal/public-sector metadata into quarantine before promotion.",
            },
            "platform_open": {
                "label": "Open Page",
                "trigger": "open_in_platform_button",
                "endpoint": "/api/platform/browser/render",
                "provider_execution_allowed": False,
                "metadata_only": False,
                "scripts_removed": True,
                "feeds_pipeline": False,
                "description": "Opens a selected public page through the same-origin governed platform render without promoting it into evidence.",
            },
        },
        "provider": state,
        "authority": authority(False),
    }


def safe_query(value: Any) -> str:
    return " ".join(str(value or "").strip().split())[:500]


def normalize_source_domain(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    parsed = urllib.parse.urlparse(text if "://" in text else f"https://{text}")
    host = (parsed.hostname or text.split("/")[0]).lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host


def build_specified_source_plan(query: str, sources: list[Any] | None = None) -> dict[str, Any]:
    source_inputs = sources or []
    planned_sources: list[dict[str, Any]] = []
    for item in source_inputs:
        candidate = item if isinstance(item, dict) else {"domain": str(item), "label": str(item)}
        record = classify_source(candidate).to_dict()
        planned_sources.append(
            {
                "source_id": record["source_id"],
                "label": record["label"],
                "domain": record["domain"],
                "source_type": record["source_type"],
                "tier": record["tier"],
                "status": record["status"],
                "query_fragment": f"site:{record['domain']}",
                "metadata_query": f"{query} site:{record['domain']}" if query and record["domain"] != "unknown" else query,
                "eligible_for_metadata_query": bool(record["allowlisted"] and not record["denylisted"]),
                "requires_operator_review": True,
                "body_read_allowed": False,
                "runtime_truth_write": "blocked",
                "reasons": record["reasons"],
            }
        )
    eligible = [item for item in planned_sources if item["eligible_for_metadata_query"]]
    return {
        "schema_version": "claire.specified_source_activation_plan.v1",
        "query": query,
        "status": "specified_sources_ready" if eligible else "no_allowlisted_specified_sources" if planned_sources else "unspecified_source_discovery",
        "specified_source_count": len(planned_sources),
        "eligible_source_count": len(eligible),
        "sources": planned_sources,
        "query_strategy": {
            "mode": "source_constrained_metadata_query" if eligible else "provider_metadata_query",
            "provider_query": " OR ".join(item["metadata_query"] for item in eligible[:4]) if eligible else query,
            "body_reads_allowed": False,
            "quarantine_required": True,
            "manual_promotion_required": True,
        },
    }


def safe_browser_url(value: Any) -> str:
    text = str(value or "").strip()
    parsed = urllib.parse.urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or host.endswith(".local"):
        return ""
    try:
        address = ip_address(host)
    except ValueError:
        address = None
    if address and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        return ""
    return text


def result_id(provider: str, query: str, url: str, rank: int) -> str:
    digest = sha256(f"{provider}|{query}|{url}|{rank}".encode("utf-8")).hexdigest()[:16]
    return f"connected-meta-{digest}"


def normalize_results(provider: str, query: str, raw_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(raw_results[:DEFAULT_MAX_RESULTS], start=1):
        url = str(item.get("url") or item.get("link") or item.get("href") or "")
        title = str(item.get("title") or item.get("name") or "Untitled result")
        snippet = str(item.get("snippet") or item.get("description") or item.get("content") or "Metadata-only search result.")
        normalized.append(
            {
                "result_id": result_id(provider, query, url, index),
                "title": title,
                "url": url,
                "provider": provider,
                "rank": index,
                "snippet": snippet,
                "query": query,
                "captured_at": utc_now(),
                "metadata_only": True,
                "body_read": False,
                "network_request_performed": True,
                "runtime_truth_mutated": False,
            }
        )
    return normalized


def http_json(url: str, *, headers: dict[str, str] | None = None, data: dict[str, Any] | None = None, timeout: int = 12) -> dict[str, Any]:
    body = None
    request_headers = {"Accept": "application/json", **(headers or {})}
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(1_000_000)
    return json.loads(raw.decode("utf-8", errors="replace"))


def http_text(url: str, *, headers: dict[str, str] | None = None, timeout: int = 12) -> str:
    request_headers = {
        "Accept": "text/html,application/xhtml+xml",
        "User-Agent": "ClaireGovernedMetadataProbe/1.0",
        **(headers or {}),
    }
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(1_000_000)
    return raw.decode("utf-8", errors="replace")


def http_html_for_browser(url: str, *, timeout: int = 12) -> str:
    request_headers = {
        "Accept": "text/html,application/xhtml+xml",
        "User-Agent": "Mozilla/5.0 ClaireGovernedPlatformBrowser/1.0",
    }
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(MAX_BROWSER_RENDER_BYTES)
        content_type = response.headers.get("content-type", "")
    text = raw.decode("utf-8", errors="replace")
    if "html" not in content_type.lower() and not text.lstrip().lower().startswith(("<!doctype", "<html")):
        escaped = html_escape(text[:200_000])
        return f"<!doctype html><html><body><pre>{escaped}</pre></body></html>"
    return text


def proxied_url(value: str) -> str:
    return "/api/platform/browser/render?url=" + urllib.parse.quote(value, safe="")


def unwrap_provider_redirect(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    query = urllib.parse.parse_qs(parsed.query)
    for key in ("uddg", "url", "u", "q"):
        for candidate in query.get(key, []):
            if safe_browser_url(candidate):
                return candidate
    return value


def absolutize_url(base_url: str, value: str) -> str:
    if not value or value.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return value
    absolute = unwrap_provider_redirect(urllib.parse.urljoin(base_url, value))
    if not safe_browser_url(absolute):
        return value
    return proxied_url(absolute)


def prepare_platform_browser_html(url: str, html: str) -> str:
    base_href = html_escape(url, quote=True)
    html = re.sub(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"\s+on[a-zA-Z]+\s*=\s*(['\"]).*?\1", "", html, flags=re.IGNORECASE | re.DOTALL)

    def replace_quoted_attr(match: re.Match[str]) -> str:
        attr = match.group(1)
        quote = match.group(2)
        value = match.group(3)
        replacement = absolutize_url(url, value)
        return f'{attr}={quote}{html_escape(replacement, quote=True)}{quote}'

    def replace_unquoted_attr(match: re.Match[str]) -> str:
        attr = match.group(1)
        value = match.group(2)
        replacement = absolutize_url(url, value)
        return f'{attr}="{html_escape(replacement, quote=True)}"'

    html = re.sub(r"\b(href|src|action)=([\"'])(.*?)(\2)", lambda m: replace_quoted_attr(m), html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"\b(href|src|action)=([^\s\"'<>]+)", lambda m: replace_unquoted_attr(m), html, flags=re.IGNORECASE)
    html = re.sub(r"\s+target\s*=\s*(['\"]).*?\1", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"\s+rel\s*=\s*(['\"]).*?\1", "", html, flags=re.IGNORECASE | re.DOTALL)
    banner = (
        "<div style=\"position:sticky;top:0;z-index:2147483647;padding:8px 12px;"
        "font:13px system-ui;background:#091830;color:#e8f0fe;border-bottom:1px solid #1a3a5c\">"
        "Claire platform browser render · scripts removed · "
        f"<a style=\"color:#00d4ff\" target=\"_blank\" rel=\"noopener\" href=\"{base_href}\">open original</a></div>"
    )
    if re.search(r"<head[^>]*>", html, flags=re.IGNORECASE):
        html = re.sub(r"<head([^>]*)>", f"<head\\1><base href=\"{base_href}\">", html, count=1, flags=re.IGNORECASE)
    else:
        html = f"<!doctype html><html><head><base href=\"{base_href}\"></head><body>{html}</body></html>"
    if re.search(r"<body[^>]*>", html, flags=re.IGNORECASE):
        html = re.sub(r"<body([^>]*)>", f"<body\\1>{banner}", html, count=1, flags=re.IGNORECASE)
    else:
        html += banner
    return html


class DuckDuckGoMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[dict[str, str]] = []
        self._active_link: dict[str, str] | None = None
        self._active_snippet = False
        self._link_text: list[str] = []
        self._snippet_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        classes = set(values.get("class", "").split())
        if tag == "a" and "result__a" in classes:
            self._active_link = {"url": decode_duckduckgo_url(values.get("href", ""))}
            self._link_text = []
        elif "result__snippet" in classes:
            self._active_snippet = True
            self._snippet_text = []

    def handle_data(self, data: str) -> None:
        if self._active_link is not None:
            self._link_text.append(data)
        if self._active_snippet:
            self._snippet_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._active_link is not None:
            title = " ".join("".join(self._link_text).split())
            url = self._active_link.get("url", "")
            if title and url:
                self.results.append({"title": title, "url": url, "snippet": ""})
            self._active_link = None
            self._link_text = []
        elif self._active_snippet:
            snippet = " ".join("".join(self._snippet_text).split())
            if snippet and self.results and not self.results[-1].get("snippet"):
                self.results[-1]["snippet"] = snippet
            self._active_snippet = False
            self._snippet_text = []


def decode_duckduckgo_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    query = urllib.parse.parse_qs(parsed.query)
    if query.get("uddg"):
        return query["uddg"][0]
    return urllib.parse.urljoin("https://duckduckgo.com", value)


def execute_duckduckgo_search(query: str, max_results: int) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"q": query})
    html = http_text(f"https://html.duckduckgo.com/html/?{params}")
    parser = DuckDuckGoMetadataParser()
    parser.feed(html)
    return parser.results[:max_results]


def execute_searchgov_search(query: str, max_results: int) -> list[dict[str, Any]]:
    affiliate = os.environ.get("SEARCHGOV_AFFILIATE", "").strip()
    access_key = os.environ.get("SEARCHGOV_ACCESS_KEY", "").strip()
    if not affiliate or not access_key:
        raise RuntimeError("Search.gov requires SEARCHGOV_AFFILIATE and SEARCHGOV_ACCESS_KEY")
    params = urllib.parse.urlencode(
        {
            "affiliate": affiliate,
            "access_key": access_key,
            "query": query,
            "limit": max(1, min(max_results, 50)),
            "enable_highlighting": "false",
        }
    )
    payload = http_json(f"https://api.gsa.gov/technology/searchgov/v2/results/i14y?{params}")
    web = payload.get("web", {}) if isinstance(payload.get("web"), dict) else {}
    results = list(web.get("results", []) or [])
    best_bets = list(payload.get("text_best_bets", []) or [])
    return [*best_bets, *results][:max_results]


class PlatformReadableParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title = ""
        self.links: list[dict[str, str]] = []
        self.blocks: list[dict[str, str]] = []
        self._tag_stack: list[str] = []
        self._active_link: dict[str, str] | None = None
        self._active_link_text: list[str] = []
        self._active_block: dict[str, Any] | None = None
        self._in_title = False
        self._title_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self._tag_stack.append(tag)
        values = {name.lower(): value or "" for name, value in attrs}
        if tag == "title":
            self._in_title = True
            self._title_text = []
        if tag == "a" and values.get("href"):
            href = absolutize_url(self.base_url, values["href"])
            if href.startswith("/api/platform/browser/render?url="):
                self._active_link = {"href": href}
                self._active_link_text = []
        if tag == "form" and values.get("action"):
            href = absolutize_url(self.base_url, values["action"])
            if href.startswith("/api/platform/browser/render?url=") and len(self.links) < 80:
                self.links.append({"href": href, "label": "Form action"})
        if tag in {"h1", "h2", "h3", "p", "li"}:
            self._active_block = {"tag": tag, "text": []}

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_text.append(data)
        if self._active_link is not None:
            self._active_link_text.append(data)
        if self._active_block is not None:
            self._active_block["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.title = " ".join("".join(self._title_text).split())[:180]
            self._in_title = False
        if tag == "a" and self._active_link is not None:
            label = " ".join("".join(self._active_link_text).split())
            if label and len(self.links) < 80:
                self.links.append({"href": self._active_link["href"], "label": label[:240]})
            self._active_link = None
            self._active_link_text = []
        if self._active_block is not None and tag == self._active_block["tag"]:
            text = " ".join("".join(self._active_block["text"]).split())
            if text and len(text) > 20 and len(self.blocks) < 80:
                self.blocks.append({"tag": tag, "text": text[:1200]})
            self._active_block = None
        if self._tag_stack:
            self._tag_stack.pop()


def build_platform_readable_document(url: str, html: str) -> str:
    html = re.sub(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<style\b[^<]*(?:(?!</style>)<[^<]*)*</style>", "", html, flags=re.IGNORECASE)
    parser = PlatformReadableParser(url)
    parser.feed(html)
    title = parser.title or urllib.parse.urlparse(url).netloc or "Platform page"
    escaped_url = html_escape(url, quote=True)
    blocks = "\n".join(
        f"<section class='read-block read-{html_escape(item['tag'])}'><p>{html_escape(item['text'])}</p></section>"
        for item in parser.blocks[:50]
    )
    links = "\n".join(
        f"<a class='read-link' href='{html_escape(item['href'], quote=True)}'>{html_escape(item['label'])}</a>"
        for item in parser.links[:60]
    )
    if not blocks:
        blocks = "<section class='read-block'><p>Claire loaded this page, but it did not expose readable static text. Use Open externally for the full interactive page.</p></section>"
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_escape(title)}</title>
  <style>
    body{{margin:0;background:#f7f9fc;color:#162033;font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
    .bar{{position:sticky;top:0;background:#091830;color:#e8f0fe;padding:10px 14px;border-bottom:1px solid #1a3a5c;z-index:10}}
    .bar strong{{display:block;font-size:14px}} .bar small{{color:#7a9cc0;word-break:break-all}}
    main{{max-width:1040px;margin:0 auto;padding:24px}}
    h1{{font-size:28px;margin:0 0 8px}} .url{{color:#5b6f88;word-break:break-all;margin-bottom:18px}}
    .read-block{{background:white;border:1px solid #d9e1ec;border-radius:8px;padding:12px 14px;margin:10px 0}}
    .read-h1 p,.read-h2 p,.read-h3 p{{font-weight:800;font-size:20px;margin:0}} p{{margin:0}}
    .links{{display:grid;gap:8px;margin-top:18px}} .read-link{{display:block;background:#eef5ff;border:1px solid #c9dcf5;border-radius:8px;padding:9px 11px;color:#064da1;text-decoration:none}}
  </style>
</head>
<body>
  <div class="bar"><strong>Claire platform browser render</strong><small>{html_escape(url)}</small></div>
  <main>
    <h1>{html_escape(title)}</h1>
    <div class="url">{html_escape(url)}</div>
    {blocks}
    <div class="links">{links}</div>
    <p class="url"><a href="{escaped_url}" target="_blank" rel="noopener">Open original externally</a></p>
  </main>
</body>
</html>"""


def execute_provider_search(provider: str, key: str, query: str, max_results: int) -> list[dict[str, Any]]:
    encoded = urllib.parse.urlencode({"q": query})
    if provider == "brave":
        payload = http_json(
            f"https://api.search.brave.com/res/v1/web/search?{encoded}&count={max_results}",
            headers={"X-Subscription-Token": key},
        )
        return list(payload.get("web", {}).get("results", []) or [])
    if provider == "bing":
        payload = http_json(
            f"https://api.bing.microsoft.com/v7.0/search?{encoded}&count={max_results}",
            headers={"Ocp-Apim-Subscription-Key": key},
        )
        return list(payload.get("webPages", {}).get("value", []) or [])
    if provider == "duckduckgo":
        return execute_duckduckgo_search(query, max_results)
    if provider == "searchgov":
        return execute_searchgov_search(query, max_results)
    if provider == "serpapi":
        params = urllib.parse.urlencode({"engine": "google", "q": query, "api_key": key, "num": max_results})
        payload = http_json(f"https://serpapi.com/search.json?{params}")
        return list(payload.get("organic_results", []) or [])
    if provider == "tavily":
        payload = http_json(
            "https://api.tavily.com/search",
            data={"api_key": key, "query": query, "max_results": max_results, "include_answer": False, "include_raw_content": False},
        )
        return list(payload.get("results", []) or [])
    return []


def quarantine_path() -> Path:
    return project_root() / "data" / "quarantine" / "connected_search_metadata"


def promoted_evidence_path() -> Path:
    return project_root() / "data" / "internet_evidence" / "promoted_metadata_evidence_store.json"


def latest_result_path() -> Path:
    return project_root() / "data" / "continuous_runtime" / "results" / "latest_result.json"


def governed_review_queue_path() -> Path:
    return project_root() / "data" / "governed_review_queue.json"


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, payload: Any) -> Any:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def write_quarantine_record(payload: dict[str, Any]) -> dict[str, str]:
    out_dir = quarantine_path()
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = out_dir / "latest_search_results.json"
    history = out_dir / f"search_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{payload['query_id']}.json"
    text = json.dumps(payload, indent=2, sort_keys=True)
    latest.write_text(text + "\n", encoding="utf-8")
    history.write_text(text + "\n", encoding="utf-8")
    return {"latest": str(latest), "history": str(history)}


def latest_quarantined_search() -> dict[str, Any]:
    return read_json(quarantine_path() / "latest_search_results.json", {})


def blocked_response(query: str, reason: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": "blocked",
        "reason": reason,
        "query": query,
        "query_id": sha256(query.encode("utf-8")).hexdigest()[:12],
        "provider": provider_state(),
        "results": [],
        "result_cards": [],
        "quarantine": {"written": False, "path": None},
        "authority": authority(False),
    }


def provider_error_response(query: str, reason: str) -> dict[str, Any]:
    payload = blocked_response(query, "provider_request_failed")
    payload["status"] = "provider_error"
    payload["provider_error"] = reason[:500]
    return payload


def build_connected_search_response(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    sources: list[Any] | None = None,
) -> dict[str, Any]:
    state = provider_state()
    source_plan = build_specified_source_plan(query, sources)
    provider_query = source_plan.get("query_strategy", {}).get("provider_query") or query
    if not query:
        return blocked_response(query, "empty_query")
    if not state["provider_known"]:
        return blocked_response(query, "provider_not_configured")
    if not state["real_provider_gate_enabled"]:
        return blocked_response(query, "real_provider_gate_disabled")
    provider_attempts = [
        item for item in state.get("provider_stack_states", []) if item.get("execution_allowed")
    ] or [
        {
            "provider": state["provider"],
            "required_key_name": state.get("required_key_name"),
            "required_key_present": state.get("required_key_present"),
            "execution_allowed": state.get("execution_allowed"),
        }
    ]
    if not any(item.get("required_key_present") for item in provider_attempts):
        return blocked_response(query, "provider_key_missing")

    provider = ""
    raw_results: list[dict[str, Any]] = []
    errors: list[str] = []
    for attempt in provider_attempts:
        provider = str(attempt.get("provider") or "")
        if provider not in PROVIDER_KEYS:
            continue
        key_name = str(PROVIDER_KEYS.get(provider) or "")
        key = os.environ.get(key_name, "") if key_name else ""
        try:
            raw_results = execute_provider_search(provider, key, provider_query, max(1, min(max_results, DEFAULT_MAX_RESULTS)))
        except Exception as exc:
            errors.append(redact_secrets(f"{provider}: {type(exc).__name__}: {exc}"))
            continue
        if raw_results:
            break
    try:
        raw_results = raw_results
    except Exception as exc:
        return provider_error_response(query, f"{type(exc).__name__}: {exc}")
    if not raw_results:
        return provider_error_response(query, "; ".join(errors) or "provider stack returned no metadata results")
    results = normalize_results(provider, provider_query, raw_results)
    quarantine_store = build_quarantine_store(results)
    payload = {
        "version": VERSION,
        "status": "metadata_results_quarantined",
        "query": query,
        "provider_query": provider_query,
        "query_id": sha256(f"{provider}|{query}|{utc_now()}".encode("utf-8")).hexdigest()[:12],
        "source_activation": source_plan,
        "provider": {**state, "provider_used": provider, "provider_errors": errors},
        "results": quarantine_store["results"],
        "result_cards": [
            {
                "title": item["title"],
                "url": item["url"],
                "snippet": item["snippet"],
                "rank": item["rank"],
                "trust_tier": item["trust_tier"],
                "source_family": item["source_family"],
                "review_state": item["review_state"],
                "quarantine_state": item["quarantine_state"],
            }
            for item in quarantine_store["results"]
        ],
        "quarantine_store": quarantine_store,
        "authority": authority(True),
    }
    paths = write_quarantine_record(payload)
    payload["quarantine"] = {"written": True, **paths}
    return payload


def promoted_evidence_store() -> dict[str, Any]:
    store = read_json(promoted_evidence_path(), {})
    if isinstance(store, dict):
        store.setdefault("schema_version", "v19.89.8_promoted_metadata_evidence_store")
        store.setdefault("status", "ready")
        store.setdefault("items", [])
        return store
    return {"schema_version": "v19.89.8_promoted_metadata_evidence_store", "status": "ready", "items": []}


def promote_latest_metadata_to_evidence(confirm_text: str, result_ids: list[str] | None = None) -> dict[str, Any]:
    latest = latest_quarantined_search()
    if confirm_text != PROMOTION_CONFIRM_TEXT:
        return {
            "status": "blocked",
            "reason": "operator_confirmation_required",
            "required_confirm_text": PROMOTION_CONFIRM_TEXT,
            "authority": authority(False),
        }
    results = latest.get("results", []) if isinstance(latest, dict) else []
    if not isinstance(results, list) or not results:
        return {"status": "blocked", "reason": "no_quarantined_metadata_available", "authority": authority(False)}

    selected = set(result_ids or [])
    promoted: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        if selected and item.get("result_id") not in selected:
            continue
        if item.get("quarantine_state") == "denied":
            continue
        promoted.append(
            {
                "evidence_id": f"evidence-{item.get('result_id')}",
                "source_result_id": item.get("result_id"),
                "query": latest.get("query", ""),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", ""),
                "provider": item.get("provider", latest.get("provider", {}).get("provider")),
                "rank": item.get("rank"),
                "source_family": item.get("source_family"),
                "trust_tier": item.get("trust_tier"),
                "evidence_state": "promoted_metadata_evidence",
                "metadata_only": True,
                "body_read_performed": False,
                "runtime_truth_write": "blocked",
                "promoted_at": utc_now(),
                "lineage": {
                    "quarantine_query_id": latest.get("query_id"),
                    "quarantine_path": str(quarantine_path() / "latest_search_results.json"),
                    "promotion_confirmed_by": "operator",
                },
            }
        )

    store = promoted_evidence_store()
    existing_ids = {item.get("evidence_id") for item in store.get("items", []) if isinstance(item, dict)}
    new_items = [item for item in promoted if item["evidence_id"] not in existing_ids]
    store["items"].extend(new_items)
    store["updated_at"] = utc_now()
    write_json(promoted_evidence_path(), store)
    return {
        "status": "promoted_to_evidence",
        "promoted_count": len(new_items),
        "total_evidence_count": len(store["items"]),
        "evidence_store": str(promoted_evidence_path()),
        "items": new_items,
        "authority": authority(False),
    }


def score_evidence_relevance(query: str, item: dict[str, Any]) -> float:
    terms = {part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in query).split() if len(part) > 2}
    text = " ".join(str(item.get(key, "")) for key in ("title", "snippet", "source_family", "trust_tier")).lower()
    if not terms:
        return 0.35
    matched = sum(1 for term in terms if term in text)
    return round(min(0.95, 0.35 + matched / max(1, len(terms)) * 0.5), 4)


def build_hybrid_result(query: str) -> dict[str, Any]:
    store = promoted_evidence_store()
    evidence = [item for item in store.get("items", []) if isinstance(item, dict)]
    query_text = safe_query(query) or str(evidence[-1].get("query", "") if evidence else "")
    relevant = [
        {**item, "relevance_score": score_evidence_relevance(query_text, item)}
        for item in evidence
        if not query_text or score_evidence_relevance(query_text, item) >= 0.35
    ]
    relevant.sort(key=lambda item: item.get("relevance_score", 0), reverse=True)
    selected = relevant[:6]
    if not selected:
        result = {
            "schema_version": "v19.89.8_hybrid_result",
            "status": "insufficient_promoted_evidence",
            "query": query_text,
            "evidence_count": 0,
            "missing_evidence": ["promoted connected-search metadata evidence"],
            "authority": authority(False),
        }
        write_json(latest_result_path(), result)
        return result

    families = sorted({str(item.get("source_family") or "unknown") for item in selected})
    top = selected[0]
    confidence = round(sum(float(item.get("relevance_score", 0.35)) for item in selected) / len(selected), 4)
    trend = {
        "title": f"{query_text or top.get('title')} signal cluster",
        "summary": f"Promoted metadata indicates activity across {', '.join(families)} sources.",
        "source_family_count": len(families),
        "evidence_count": len(selected),
    }
    gap = {
        "title": "Evidence-backed market intelligence gap",
        "summary": "Claire has enough metadata to form a review candidate, but body-level claims remain blocked until one-shot body read approval.",
        "missing_evidence": ["body-level verification", "second-source corroboration"] if len(families) < 2 else ["body-level verification"],
    }
    candidate = {
        "candidate_id": "hybrid-candidate-" + sha256(f"{query_text}|{top.get('evidence_id')}".encode("utf-8")).hexdigest()[:12],
        "title": f"Governed opportunity review: {query_text or top.get('title')}",
        "candidate_type": "portfolio",
        "status": "pending_operator_review",
        "confidence": confidence,
        "source_evidence_ids": [item.get("evidence_id") for item in selected],
        "runtime_truth_write": "blocked",
    }
    result = {
        "schema_version": "v19.89.8_hybrid_result",
        "status": "hybrid_result_ready_for_review",
        "generated_at": utc_now(),
        "query": query_text,
        "mode": "hybrid_connected_metadata_plus_deterministic_governance",
        "evidence_count": len(selected),
        "evidence": selected,
        "trend": trend,
        "gap": gap,
        "candidate": candidate,
        "review_status": "pending_operator_review",
        "authority": authority(False),
    }
    write_json(latest_result_path(), result)
    append_hybrid_result_to_review_queue(result)
    return result


def append_hybrid_result_to_review_queue(result: dict[str, Any]) -> None:
    path = governed_review_queue_path()
    queue = read_json(path, {"queue": [], "decisions": []})
    if not isinstance(queue, dict):
        queue = {"queue": [], "decisions": []}
    queue.setdefault("queue", [])
    candidate = result.get("candidate", {})
    existing = {item.get("review_item_id") or item.get("id") for item in queue["queue"] if isinstance(item, dict)}
    review_id = candidate.get("candidate_id")
    if review_id not in existing:
        queue["queue"].append(
            {
                "review_item_id": review_id,
                "id": review_id,
                "status": "pending_review",
                "headline": candidate.get("title"),
                "query": result.get("query"),
                "candidate": candidate,
                "evidence_count": result.get("evidence_count", 0),
                "allowed_decisions": ["approve_for_portfolio_preview", "reject", "request_more_evidence"],
                "runtime_truth_write": "blocked",
                "created_at": utc_now(),
            }
        )
    queue["updated_at"] = utc_now()
    write_json(path, queue)


@router.get("/api/search/provider/status")
def get_connected_search_provider_status() -> dict[str, Any]:
    state = provider_state()
    stack_ready = bool(state.get("execution_allowed") or any(
        item.get("execution_allowed") for item in state.get("provider_stack_states", [])
    ))
    return {"version": VERSION, "status": "ready" if stack_ready else "blocked", "provider": state, "authority": authority(False)}


@router.get("/api/search/lane-config")
def get_search_lane_config() -> dict[str, Any]:
    return search_lane_config()


@router.post("/api/search/provider/query")
async def post_connected_search_provider_query(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    body = body if isinstance(body, dict) else {}
    query = safe_query(body.get("query"))
    max_results = int(body.get("max_results") or DEFAULT_MAX_RESULTS)
    sources = body.get("sources") or body.get("source_domains") or body.get("specified_sources")
    return build_connected_search_response(query, max_results, sources if isinstance(sources, list) else None)


@router.get("/api/platform/browser/render", response_class=HTMLResponse)
def get_platform_browser_render(url: str = "") -> HTMLResponse:
    safe_url = safe_browser_url(url)
    if not safe_url:
        return HTMLResponse(
            "<!doctype html><html><body style='font:16px system-ui;padding:24px'>"
            "<h1>Claire blocked this browser request</h1>"
            "<p>Only public http/https pages can be opened in the governed platform view.</p>"
            "</body></html>",
            status_code=400,
            headers={"Cache-Control": "no-store"},
        )
    try:
        html = http_html_for_browser(safe_url)
        rendered = build_platform_readable_document(safe_url, html)
    except Exception as exc:
        rendered = (
            "<!doctype html><html><body style='font:16px system-ui;padding:24px;background:#f7f8fb;color:#1c2530'>"
            "<h1>Claire could not render this page in-platform</h1>"
            f"<p>{html_escape(type(exc).__name__)}: {html_escape(str(exc))}</p>"
            f"<p><a href='{html_escape(safe_url, quote=True)}' target='_blank' rel='noopener'>Open original externally</a></p>"
            "</body></html>"
        )
    return HTMLResponse(
        rendered,
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src http: https: data: blob: 'unsafe-inline'; script-src 'none'; frame-ancestors 'self'",
        },
    )


@router.post("/api/search/evidence/promote")
async def post_promote_connected_metadata_to_evidence(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    body = body if isinstance(body, dict) else {}
    result_ids = body.get("result_ids")
    return promote_latest_metadata_to_evidence(
        confirm_text=str(body.get("confirm_text") or ""),
        result_ids=[str(item) for item in result_ids] if isinstance(result_ids, list) else None,
    )


@router.post("/api/cockpit/hybrid/result")
async def post_build_hybrid_connected_result(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        body = {}
    body = body if isinstance(body, dict) else {}
    return build_hybrid_result(safe_query(body.get("query")))


@router.get("/api/cockpit/hybrid/latest")
def get_latest_hybrid_connected_result() -> dict[str, Any]:
    return read_json(latest_result_path(), {"status": "empty", "authority": authority(False)})
