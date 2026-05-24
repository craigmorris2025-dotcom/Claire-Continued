| Route | What | Why | When | Trigger Source | Required Scores | Sequence | Output | Failure State |

|---|---|---|---|---|---|---|---|---|

| Portfolio | Portfolio action/optimization | Market evidence impacts portfolio | Market/thesis relevance passes | trend + market + portfolio signal | trend\_strength, thesis\_quality, portfolio\_relevance, risk\_exposure | 23 → 26 → 27 | portfolio artifact | generic/easy output |

| Breakthrough | Escalation | Discovery exceeds normal market route | gap + discovery + breakthrough threshold pass | discovery/gap/breakthrough | gap\_validity, gap\_severity, breakthrough\_threshold | 11 → 12 → 13 → 14 → 15 | breakthrough classification | strong signal stays portfolio-only |

| Tech Design Build | Buildable-now/design route | Tech breakthrough requires construction path | trend → discovery → breakthrough → innovation conditions pass | breakthrough classification + innovation path | technology\_signal, breakthrough\_threshold, buildability\_readiness, design\_route\_readiness | 15 → 16 → 17 → 18 → 19 → 20 → 21 → 22 | design portal contract, CAD intent | design route not triggered or triggers too early |

| Acquisition | Buyer/acquirer package | Strategic value exists | moat/value/acquirer-fit pass | thesis + business model + acquirer signal | moat, value\_capture, acquirer\_fit | 24 → 25 → 28 → 29 → 30 | acquisition package | package is generic |

| Recursive Memory | Future intelligence | Approved output should strengthen future runs | output approved and replayable | operator approval + evidence lineage | output\_quality, traceability, replayability | output → memory → replay | improved future runs | memory commits unapproved output |

