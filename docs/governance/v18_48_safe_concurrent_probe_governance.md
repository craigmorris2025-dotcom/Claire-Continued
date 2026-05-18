# v18.48 Safe Concurrent Probe Governance

This build adds the first bounded concurrency governance layer for Claire's governed live web/search path.

## What it enables

- Policy evaluation for safe concurrent probe batches.
- Operator-visible review payloads.
- Manual-enable controlled bounded concurrency.
- Fail-closed denial when policy is missing, malformed, or exceeded.

## Manual environment flag

```bat
set CLAIRE_ALLOW_SAFE_CONCURRENT_PROBES=1
set CLAIRE_MAX_CONCURRENT_PROBES=2
set CLAIRE_MAX_CONCURRENT_PROBE_BATCH=5
```

PowerShell:

```powershell
$env:CLAIRE_ALLOW_SAFE_CONCURRENT_PROBES="1"
$env:CLAIRE_MAX_CONCURRENT_PROBES="2"
$env:CLAIRE_MAX_CONCURRENT_PROBE_BATCH="5"
```

## Still explicitly disabled

- Autonomous execution.
- Automatic updates.
- Runtime truth mutation.
- Unbounded concurrency.
- Unrestricted body fetching.
- Unsupervised provider execution.

## Next build

v18.49 = Governed Search Evidence Basket
