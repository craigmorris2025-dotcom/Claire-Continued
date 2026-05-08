# Claire v17.43 — Persistent Internet Campaigns + Update Cycles

This package turns the v17.41/v17.42 internet runtime into persistent manually refreshable campaigns.

## Capabilities

- Create named internet campaigns
- Save campaign state
- Refresh campaign evidence on demand
- Link refreshes into the v17.42 runtime integration path
- Compare new evidence against prior evidence
- Detect confidence drift, source changes, new evidence, and stable evidence state
- Save refresh reports
- Provide CLI and API routes

## CLI

```bash
python -m claire.persistent_internet_campaigns.cli create --name "AI policy watch" --query "AI disclosure rules" --url https://www.sec.gov/newsroom
python -m claire.persistent_internet_campaigns.cli list
python -m claire.persistent_internet_campaigns.cli refresh --campaign-id campaign_x
```

## FastAPI Wiring

```python
from claire.persistent_internet_campaigns.api_routes import router as internet_campaigns_router
app.include_router(internet_campaigns_router)
```

## Boundary

This package does not install a hidden background scheduler. Refresh is explicit through CLI/API. That keeps the system safe and auditable while making update cycles real.
