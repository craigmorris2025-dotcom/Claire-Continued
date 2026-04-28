# Claire Syntalion — API Reference

Base URL: `http://localhost:8000`

## Pipeline

### POST /evaluate
Run the full 24-engine evaluation pipeline.

**Request Body:**
```json
{
  "input_text": "Target description text (3-50000 chars)",
  "mode": "deterministic|connected|hybrid",
  "request_type": "evaluate|analyze|plan|construct",
  "source": "api|ui|cli",
  "priority": "low|medium|high"
}
```

**Response:**
```json
{
  "run_id": "run-abc123",
  "status": "success",
  "mode": "deterministic",
  "decision_classification": "GO|CAUTION|NO-GO",
  "breakthrough_classification": "HIGH|MODERATE|LOW",
  "scores": { "semantic_score": 0.72, ... },
  "acquirer_matches": [...],
  "domain": "technology",
  "keywords": ["quantum", "encryption"],
  "domain_scores": { "defense": 0.85, ... },
  "syntalion_ready": true,
  "confidence": 0.66
}
```

### GET /scorecard/{run_id}
Formatted scorecard for a completed run.

## History

### GET /history?limit=25&offset=0
Pipeline run history (newest first).

### GET /history/{run_id}
Full details for a single run.

### GET /stats
Aggregate statistics across all runs.

## Acquirers

### GET /acquirers?sector=defense
List strategic acquirer profiles (optional sector filter).

### GET /acquirers/{ticker}
Single acquirer profile by ticker symbol.

## System

### GET /health
Comprehensive health check (engines, phases, semantic, connectors, acquirers, database, bridge, modes).

### GET /modes
Available operating modes with capabilities.

### GET /engines
All 24 engines grouped by phase.

## Connectors

### POST /connectors/fetch
Fetch data from a connector.

```json
{
  "connector": "market|patent|financial",
  "mode": "connected",
  "sector": "technology"
}
```

### GET /connectors/status
Status of all registered connectors.

## Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
