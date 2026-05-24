# Runtime Core Migration Release Notes

## Summary

The runtime canonicalization migration moves active backend ownership to `runtime_core`, keeps `backend` as the ASGI adapter boundary, and preserves `claire/__init__.py` as an intentional tombstone.

## Release Invariants

- Route count: `353`
- Dashboard assets: `/dashboard`, platform CSS, and platform JS load successfully
- Activation registry: `14/14` pipelines ready
- Active imports/config: no legacy runtime imports and no legacy env references outside archive/report/data areas
- Tombstone: legacy `claire` namespace raises a clear import error

## Dependency Scan Follow-Up

The SCA pass identified fixed-version upgrades for `idna` and `starlette`; the pinned requirements now use the fixed versions. The local pip executable was upgraded in the venv for scan hygiene.

## Operator Notice

`claire` tombstone present; removal planned after 2 releases or 30 days. External systems should migrate to `runtime_core` and `PLATFORM_*` configuration now.
