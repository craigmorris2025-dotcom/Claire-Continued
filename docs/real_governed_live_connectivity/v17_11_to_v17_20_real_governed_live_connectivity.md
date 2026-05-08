# Claire v17.11-v17.20 Real Governed Live Connectivity Layer

This build moves Claire from connectivity contracts toward real governed live-connectivity readiness.

## Included Builds

- v17.11 Governed HTTP Client Adapter
- v17.12 Governed Search Adapter Contract
- v17.13 Rate Limit Guard
- v17.14 Content Normalizer
- v17.15 Evidence Persistence
- v17.16 Retry and Dead-Letter Manager
- v17.17 Live Ingestion Worker
- v17.18 Source Policy Bridge
- v17.19 Runtime Contract
- v17.20 Live Connectivity Regression Lock

## Safety Boundary

Live HTTP exists behind an explicit `live_enabled` toggle.

Default behavior is:

```python
RealGovernedLiveConnectivityRuntime(live_enabled=False)
```

This verifies the complete governed contract path without making live network calls.

To enable real HTTP later, instantiate with:

```python
RealGovernedLiveConnectivityRuntime(live_enabled=True)
```

Only allowlisted domains fetch automatically. Unknown domains return `review_required`.
