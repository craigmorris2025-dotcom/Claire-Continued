# Trigger Score Route Map

Verified date: 2026-05-24

The trigger-score-route map is encoded in `claire/pipeline/activation_registry.py` as `PIPELINE_TRIGGER_SCORE_ROUTE`.

The current canonical route families are:

| route | primary pipelines | sequence | output |
|---|---|---:|---|
| `portfolio` | `knowledge_ingestion`, `signal_extraction`, `market_formation`, `portfolio_optimization`, `productization_path` | 1-10, 23, 26, 27, 30 | portfolio artifact |
| `breakthrough` | `market_gap`, `breakthrough_synthesis` | 11-15 | breakthrough classification |
| `tech_design_build` | `technology_intelligence`, `technical_feasibility`, `system_design`, `auto_design` | 15-22 | design portal contract and CAD intent |
| `acquisition` | `acquirer_matching`, `deal_exit_modeling` | 28-30 | acquisition package |
| `recursive_memory` | `export_package` | 30, memory, replay | traceable final package and replay candidate |

Representative selector proof is exposed by `select_pipeline_route(...)` and covered by `tests/test_pipeline_activation_registry.py`.

The map is intentionally declarative. It selects the pipeline route family and pipeline owners; it does not perform live web execution, mutate runtime truth, export CAD artifacts, or auto-install updates.
