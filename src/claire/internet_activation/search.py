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
