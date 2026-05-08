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
