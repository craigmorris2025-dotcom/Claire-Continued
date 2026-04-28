# Claire Syntalion — Architecture Guide

## Overview

Claire Syntalion is a **sovereign autonomous R&D evaluation platform** built on the
CLAIRE cognitive architecture. It processes unstructured input through a 24-engine
pipeline to produce calibrated investment/acquisition decision intelligence.

## Cognitive Architecture: CLAIRE

The system implements a 4-phase cognitive pipeline:

### Phase 1: Contract Layer
- **ClaireIntent** — validates and structures incoming requests
- **ContractValidator** — enforces schema rules (mode, type, input length)
- All data flows through typed dataclass contracts

### Phase 2: Orreadir Layer
- **OrreadirRouter** — routes requests by type (evaluate/analyze/plan/construct)
- Priority signals (high/low) and mode constraints
- Route decisions include engine selection hints

### Phase 3: Core Processing
- **Planner** — generates strategy-specific execution plans
- **DataEngine** — loads and queries 12 strategic acquirer profiles
- **SemanticLayer** — 8-domain lexicon analysis, entity extraction, confidence scoring
- **Gateway** — output formatting (JSON, summary, file export)

### Phase 4: Orchestrator
- **PipelineOrchestrator** — runs all 24 engines in 6-phase sequence
- **PatternRecognition** — detects cross-domain signal clusters
- **FeTTiom** — temporal weighting with sigmoid smoothing
- **Desking** — 4-channel distribution (executive, technical, acquirer, compliance)

### MasterPass Bridge
5-stage handoff: **Prep → Call → Normalize → Post → Assert**
- Validates result completeness
- Normalizes all scores to 0.0–1.0
- Enriches with compliance data
- Final readiness gate for Syntalion handoff

## Engine Pipeline (24 Engines, 6 Phases)

| Phase | Engines |
|-------|---------|
| 1. Ingestion & Semantic | semantic, ingestion, entity_extraction |
| 2. Intel & Scoring | market, synergy, strategy, risk, competitive, sentiment, fusion |
| 3. Strategic Analysis | acquirer_matching, benchmark, regulatory, supply_chain |
| 4. Innovation & Breakthrough | innovation, breakthrough, patent_analysis, discovery |
| 5. Deal Construction | deal, negotiation, valuation, forecasting |
| 6. Portfolio & Compliance | portfolio, compliance, decision, predictive |

## Operating Modes

| Mode | Description | Capabilities |
|------|-------------|--------------|
| Deterministic | Air-gapped | Local data only, no external calls |
| Connected | Live data | External connectors active |
| Hybrid | Full capability | All features enabled |

## Data Flow

```
Input Text → Contract Validation → Orreadir Routing → Planning
  → Semantic Analysis → 24-Engine Pipeline (6 phases)
  → Pattern Recognition → FeTTiom → Desking
  → Score Calibration → Interpretation
  → MasterPass Bridge → Persistence → API Response
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, SQLite
- **Frontend**: HTML5, Bootstrap 5, Chart.js, vanilla JavaScript
- **Architecture**: MVC, modular, async API
