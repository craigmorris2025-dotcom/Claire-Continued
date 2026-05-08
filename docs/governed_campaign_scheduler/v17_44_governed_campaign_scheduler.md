# Claire v17.44 — Governed Campaign Scheduler + Update Runner

This package adds a safe, explicit scheduler for v17.43 persistent internet campaigns.

## Capabilities

- Create campaign schedules
- Detect due campaigns
- Run due refreshes on demand
- Prevent overlapping scheduler runs with a lock file
- Save scheduler reports
- Provide CLI and API routes

## CLI

```bash
python -m claire.governed_campaign_scheduler.cli schedule --campaign-id campaign_x --cadence-minutes 1440
python -m claire.governed_campaign_scheduler.cli run-due
python -m claire.governed_campaign_scheduler.cli list
python -m claire.governed_campaign_scheduler.cli reports
```

## Windows Task Scheduler

This package does not install a background service. To automate safely, attach this command to Windows Task Scheduler:

```bash
python -m claire.governed_campaign_scheduler.cli run-due
```

## FastAPI Wiring

```python
from claire.governed_campaign_scheduler.api_routes import router as internet_scheduler_router
app.include_router(internet_scheduler_router)
```
