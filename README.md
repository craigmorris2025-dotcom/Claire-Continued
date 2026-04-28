# Claire-Syntalion v4.2 — Sovereign R&D Platform

**Web-Capable | Self-Healing | Auto-Bootstrap**

24-engine autonomous evaluation pipeline with CLAIRE cognitive architecture.

## Quick Start

### Option A: Double-Click Launch (Recommended)
1. Double-click `LAUNCH.bat` (Windows)
2. Browser opens automatically to `http://localhost:8000/ui`

### Option B: Web Bootstrap
1. Double-click `claire-bootstrap.html` in your browser
2. Follow the on-screen steps
3. Run `LAUNCH.bat` when prompted — the page auto-detects when the server starts

### Option C: Manual Launch
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m src.backend
```

## What's New in v4.2

### Web Capability
- **WebFetcher** (`src/backend/connectors/web_fetcher.py`) — Universal HTTP client with caching, rate limiting, retry logic
- **Web Proxy API** (`/api/proxy/get`, `/api/proxy/post`) — Frontend can make outbound requests through the backend (no CORS issues)
- **Connectivity Check** (`/api/proxy/ping`) — Test internet connectivity from the UI

### Self-Update System
- **Update API** (`/api/update/status`, `/api/update/apply`) — Check for and apply updates from a remote manifest
- **Frontend Updater** (`updater.js`) — Auto-checks hourly, shows notification badge when updates available
- **Version Tracking** (`data/version.json`) — Local version hash for delta comparison

### Self-Healing Bootstrap
- **Enhanced LAUNCH.bat** — 7-step bootstrapper that finds Python, creates venv, installs deps, creates directories, launches server
- **claire-bootstrap.html** — Browser-based launcher that polls for backend and auto-opens UI

## Architecture

```
Claire-Syntalion v4.2
├── claire-bootstrap.html          # Web-based installer/launcher
├── LAUNCH.bat                     # Self-healing Windows launcher
├── src/
│   ├── backend/
│   │   ├── server.py              # FastAPI app factory (v4.2)
│   │   ├── api/
│   │   │   ├── routes_pipeline.py # Pipeline evaluation API
│   │   │   ├── routes_update.py   # ★ Self-update API
│   │   │   ├── routes_proxy.py    # ★ Web proxy API
│   │   │   └── ...
│   │   ├── connectors/
│   │   │   ├── web_fetcher.py     # ★ Universal HTTP client
│   │   │   ├── market.py          # Market data connector
│   │   │   ├── patent.py          # Patent data connector
│   │   │   ├── financial.py       # Financial data connector
│   │   │   └── ...
│   │   ├── engines/               # 24 evaluation engines
│   │   ├── claire/                # CLAIRE cognitive layers
│   │   ├── orchestrator/          # Pipeline orchestration
│   │   ├── governance/            # Audit & policy
│   │   └── ...
│   └── frontend/
│       ├── index.html             # SPA dashboard
│       └── js/
│           ├── web_connector.js   # ★ Browser-side web access
│           ├── updater.js         # ★ Self-update UI
│           └── ...
├── data/                          # Runtime data + cache
├── docs/                          # API reference, architecture
└── tests/                         # Test suite
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ui` | GET | Main dashboard UI |
| `/docs` | GET | Swagger API documentation |
| `/api/health` | GET | Health check |
| `/api/pipeline/evaluate` | POST | Run evaluation pipeline |
| `/api/connectors/status` | GET | Connector status |
| `/api/proxy/get` | GET | Web proxy (GET) |
| `/api/proxy/post` | POST | Web proxy (POST) |
| `/api/proxy/ping` | GET | Connectivity test |
| `/api/update/status` | GET | Check for updates |
| `/api/update/apply` | POST | Apply available update |

## Configuration

Copy `.env.example` to `.env` and configure:

```env
CLAIRE_ENV=development
CLAIRE_PORT=8000
CLAIRE_HOST=127.0.0.1
CLAIRE_LOG_LEVEL=INFO
CLAIRE_CORS_ORIGINS=*
CLAIRE_MARKET_API_KEY=
CLAIRE_PATENT_API_KEY=
CLAIRE_FINANCIAL_API_KEY=
```

## License

Proprietary — Craig Morris / SAISS-ACS2-Syntalion
