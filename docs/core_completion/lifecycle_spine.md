# Lifecycle Spine

The v5.89.5 lifecycle spine adds a canonical 30-stage registry and runner without replacing the legacy 21-stage lifecycle surface.

Core files:

- `src/claire/lifecycle/lifecycle_registry.py`
- `src/claire/lifecycle/lifecycle_context.py`
- `src/claire/lifecycle/stage_status.py`
- `src/claire/lifecycle/lifecycle_runner.py`

Pipeline integration:

- `PipelineOrchestrator.execute()` still returns legacy `lifecycle`, `lifecycle_stages`, and `lifecycle_summary`.
- New canonical output is exposed as `core_lifecycle`, `core_lifecycle_stages`, `core_lifecycle_summary`, and `core_completion_gate`.

This keeps Evaluate / Discover / Monitor consumers stable while allowing core completion work to inspect all 30 stages.
