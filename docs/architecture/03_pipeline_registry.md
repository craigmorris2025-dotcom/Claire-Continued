# Pipeline Registry

Verified date: 2026-05-24

The ACS2 pipeline activation registry is the canonical backend-owned registry for pipeline readiness and route execution ownership.

Active owner:

- `claire/pipeline/activation_registry.py`
- API surface: `GET /api/pipelines/activation`
- Dashboard payload field: `pipeline_activation`

Every pipeline entry now exposes:

- `what`
- `why`
- `when`
- `trigger`
- `score`
- `route`
- `sequence`
- `output`
- `failure_state`
- `owner_file`

This keeps ACS2 from being a presence-only inventory. The registry now declares which trigger activates each pipeline, which score family gates it, which route owns the output, and what failure state blocks advancement.

Runtime authority remains governed:

- network execution is not enabled by the registry
- runtime truth mutation is not enabled by the registry
- dashboard rendering is read-only
- route outputs still depend on lifecycle gates and proof status
