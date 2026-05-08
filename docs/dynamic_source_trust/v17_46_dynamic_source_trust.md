# Claire v17.46 — Dynamic Source Trust + Reputation Intelligence

This package makes Claire's internet evidence weighting adaptive over time.

## Capabilities

- Source trust profiles
- Static base trust by known authoritative domains
- Adaptive trust score updates
- Positive/negative/contradiction/correction trust events
- Source quarantine
- Source release
- Evidence confidence reweighting
- Batch evidence weighting
- CLI and FastAPI routes

## CLI

```bash
python -m claire.dynamic_source_trust.cli event --domain sec.gov --event-type confirmed --confidence 0.9
python -m claire.dynamic_source_trust.cli quarantine --domain bad.example
python -m claire.dynamic_source_trust.cli profiles
```

## FastAPI Wiring

```python
from claire.dynamic_source_trust.api_routes import router as source_trust_router
app.include_router(source_trust_router)
```

## Boundary

This package does not automatically ban sources without recorded trust events or manual quarantine. It adjusts source weighting and quarantine status through explicit evidence outcome signals.
