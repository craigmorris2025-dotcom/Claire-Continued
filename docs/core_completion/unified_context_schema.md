# Unified Context Schema

`LifecycleContext` contains:

- `run_id`
- `route`
- `stage_outputs`
- `stage_statuses`
- `errors`
- `warnings`
- `metadata`
- `evidence`
- `confidence`
- `final_outputs`

Allowed stage statuses:

- `pending`
- `running`
- `complete`
- `failed`
- `insufficient_data`
- `blocked`
- `skipped_by_route`

The context is serialized inside `core_lifecycle.context` so lifecycle execution is visible and testable.
