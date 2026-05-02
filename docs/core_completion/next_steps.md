# Next Steps

Recommended next core-completion work:

1. Add compatibility shims or update legacy tests for `backend.*` imports so full pytest can collect.
2. Add a formal backend health probe that starts the configured server and checks health/status endpoints.
3. Add a dashboard load probe for `tools/serve_export_dashboard.py`.
4. Add repeated run checks for Evaluate, Discover, and Monitor mode surfaces.
5. Extend signal governance from skeleton to real source provenance only after launch stability is proven.
6. Keep v5.98 evidence/replay and v5.99 lifecycle memory as later phases.
