# Claire Cognitive Research & Web Intelligence Engine

## Definition

Claire Search is not a dashboard keyword search box. It is a Cognitive Research and Web Intelligence input layer for the lifecycle.

Its target flow is:

Search / research -> evidence -> governed signals -> entity and signal extraction -> trend discovery -> thesis formation -> portfolio, breakthrough, design, or package route.

At core completion, the implementation is intentionally minimum viable and route-safe. It supports internal search, technology search, source governance, evidence capture, and conversion of saved research into pipeline-ready governed signal candidates. Live web search is adapter-gated and returns a clear unavailable state until a configured provider exists.

## Current UI Surface

The dashboard now includes a top-level `Research` tab beside Run, Discover, Trend, Portfolio, Breakthrough, Design, Packages, Monitor, and System.

The Research surface includes:

- command search bar for natural-language research requests
- source scope selector: Web, Runs, Signals, Trends, Portfolio, Breakthroughs, Technologies, Designs, Packages, System, All
- Claire-ranked result cards
- relevance, source credibility, freshness, entities, signals, and related lifecycle route
- actions for Open, Save Evidence, Send Scan, Trend, Portfolio, Breakthrough, AutoDesign, and Package
- evidence basket
- send basket to pipeline action
- clear empty and unavailable states

## Backend Modules

Implemented under `src/claire/research/`:

- `research_result.py`: structured result contract for internal, technology, and future web research results
- `source_governance.py`: credibility, freshness, and source-policy scoring
- `web_search_adapter.py`: live web adapter interface with explicit unavailable behavior
- `evidence_basket.py`: persistent evidence collection and pipeline input conversion
- `research_service.py`: orchestrates scoped search, result ranking, evidence save, and send-to-pipeline markers
- `__init__.py`: package exports

Dashboard API routes were added in `tools/serve_export_dashboard.py`:

- `GET /api/research/evidence`
- `POST /api/research/search`
- `POST /api/research/evidence/add`
- `POST /api/research/evidence/clear`
- `POST /api/research/evidence/pipeline-input`
- `POST /api/research/send-to-pipeline`

## Source Governance

Every research result carries:

- source type
- source credibility
- freshness score
- governance status
- source policy

Live web results are not fabricated. Until live web search is configured, web-scope search returns:

`Live web search not configured yet.`

## Evidence Basket

The evidence basket persists saved sources under `data/research/evidence_basket.json`.

Saved evidence can be converted into lifecycle input using the pipeline-input endpoint. The current minimum viable conversion emits governed signal candidates using extracted signals and result summaries.

## Internal Search Coverage

Current scoped search covers:

- run history and exported `core_run_output.json` summaries through the export browser
- package/export artifacts
- technology catalog entries
- stack recommendations and component matches
- local JSON/JSONL signal-like data under `data/`

## Technology Integration

Technology search connects to the Technology Intelligence layer:

- technology catalog search
- suggested app/software/platform stack
- component matches
- compatibility and dependency metadata
- design-route lifecycle mapping

This supports AutoDesign and Design Portal routes without making design the default.

## Pipeline Integration

Research results can be sent to lifecycle routes as markers:

- scan
- trend discovery
- portfolio review
- breakthrough review
- AutoDesign
- package

The current implementation prepares governed signal candidates and route markers. It does not yet automatically launch a full lifecycle run from a research result without the user command surface.

## Current Limitations

- Live open-web search is not configured.
- Page browsing and text extraction are adapter interfaces only.
- Patent, filing, paper, repository, and news search are not yet live source integrations.
- Source comparison and contradiction detection are future layers.
- Semantic memory search is not yet implemented.
- Research-to-pipeline is currently a governed input handoff, not autonomous multi-source research execution.

## Validation Results

Rate-safe checks completed:

- targeted Python syntax check for research modules and dashboard server: passed
- dashboard JavaScript syntax check: passed
- dashboard served successfully on `http://127.0.0.1:8765`
- Research tab static assets served
- technology-scope research returned Claire-ranked technology results
- runs-scope research returned prior run results
- web-scope research returned the correct unavailable state
- evidence save endpoint worked
- evidence basket converted saved evidence into governed signal candidates

No full regression suite was run because quick checks passed and the current build guidance is rate-safe validation only.

## Next Build Steps

Safest next step:

Connect Research evidence handoff into the existing Run command payload so a saved evidence basket can seed a scan run without bypassing governance.

Later expansion:

- configured web provider
- source browsing and page reader
- source comparison and contradiction detection
- patents, filings, papers, repositories, and news adapters
- research task history
- watchlists and alerts
- recursive search across Claire memory and prior lifecycle outputs
