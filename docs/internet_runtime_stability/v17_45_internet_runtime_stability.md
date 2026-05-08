# Claire v17.45 — Internet Runtime Stability + Failure Recovery

This package adds launch-critical reliability around Claire's governed internet update operations.

## Capabilities

- Retry policy
- Failure classification
- Degraded-mode handling
- Recovery journal
- Stability run reports
- Internet runtime health checks
- Safe wrapper around campaign refresh
- Safe wrapper around scheduler run-due
- CLI and FastAPI routes

## CLI

```bash
python -m claire.internet_runtime_stability.cli health
python -m claire.internet_runtime_stability.cli refresh-campaign --campaign-id campaign_x
python -m claire.internet_runtime_stability.cli run-due
python -m claire.internet_runtime_stability.cli failures
python -m claire.internet_runtime_stability.cli reports
```

## FastAPI Wiring

```python
from claire.internet_runtime_stability.api_routes import router as internet_stability_router
app.include_router(internet_stability_router)
```

## Boundary

This package does not bypass governance blocks. It does not retry blocked/review-required sources. It makes internet updates more reliable without making unsafe actions automatic.
