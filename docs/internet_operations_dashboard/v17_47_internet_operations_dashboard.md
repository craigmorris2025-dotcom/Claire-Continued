# Claire v17.47 — Internet Operations Dashboard Layer

This package adds an operational dashboard API and standalone local HTML dashboard for Claire's governed internet runtime.

## FastAPI Wiring

```python
from claire.internet_operations_dashboard.api_routes import router as internet_ops_dashboard_router
app.include_router(internet_ops_dashboard_router)
```

## Routes

- `GET /internet/ops/snapshot`
- `POST /internet/ops/run-due`
- `POST /internet/ops/campaigns/{campaign_id}/refresh`
- `GET /internet/ops/dashboard`
