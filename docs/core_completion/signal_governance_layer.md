# v5.89.7 Signal Governance Layer

Status: implemented as a small core-completion skeleton.

Scope:

- No new connectors.
- No UI redesign.
- No endpoint renames.
- No v5.90+ breakthrough escalation changes.

Implemented files:

- `src/claire/signals/source_weighting.py`
- `src/claire/signals/signal_deduplication.py`
- `src/claire/signals/signal_scoring.py`
- `src/claire/signals/signal_governance.py`
- `src/claire/signals/__init__.py`

Capabilities:

- Normalizes raw run input into governed signal records.
- Deduplicates repeated run-level signals.
- Applies conservative source weighting.
- Scores freshness, relevance, weak-signal terms, momentum terms, agreement, quality, and noise.
- Marks signals as `safe_for_lifecycle` when quality and noise gates pass.
- Exposes `governed_signals` in pipeline output.
- Adds governed signal evidence to `core_lifecycle.context.evidence`.

Relationship to existing feed layer:

- Existing public/feed signal normalization remains under `src/claire/feeds`.
- v5.89.7 governs run-level signal basis first.
- Connected/feed-specific governance remains a later extension and should reuse existing feed contracts.

Validation:

- Focused Python syntax check passed for changed signal, lifecycle, pipeline, and contract files.
- Focused regression passed: `tests/regression/test_signal_governance.py` and `tests/regression/test_core_lifecycle.py`.
