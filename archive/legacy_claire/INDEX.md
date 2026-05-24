# Legacy Claire Archive

This archive is the landing zone for historical Claire-branded reports, handoff notes, and migration-era artifacts that are no longer part of the active runtime surface.

Active code now lives under `runtime_core`. The `claire` package remains only as a tombstone during the deprecation window so missed integrations fail clearly instead of silently loading stale runtime code.

Keep archived artifacts review-only. Do not import from this directory, mount routes from it, or use it as a source for active configuration.
