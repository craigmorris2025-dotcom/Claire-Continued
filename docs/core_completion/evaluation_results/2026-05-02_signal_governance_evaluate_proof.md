# v5.89.7 Signal Governance Evaluate Proof

Date: 2026-05-02

Governing reference:

- `C:/Users/craig/OneDrive/Documents/Claire_Master_System_Build_Plan_v5_89_5_to_v5_99.docx`

## Input Used

`Evaluate climate insurance repricing pressure, regional withdrawal, risk-transfer demand, and underwriting workflow lag as governed signals for portfolio opportunity discovery.`

Request context:

- Workflow: Evaluate
- Execution mode: deterministic
- Market universe: custom_universe
- Industry domain: insurance
- Buyer segment: enterprise_c_suite
- Objective: evaluate_opportunity

## Route Selected

- Core lifecycle route: `breakthrough_design`
- Mode decision: deterministic, connected ingestion disabled, deterministic fallback allowed
- Redline governance: allow

## Lifecycle Stages Reached

- Core lifecycle stage count: 30
- Complete stages: 29
- Skipped by route: 1
- Completion gate: complete
- Governed signal evidence embedded in `core_lifecycle.context.evidence.governed_signals`: yes

## Governed Signal Output

- Governance status: success
- Raw signals: 1
- Deduped signals: 1
- Accepted lifecycle-safe signals: 1
- First governed signal ID: `sig_0476fe799ce0`
- First governed signal quality score: 0.789
- First governed signal relevance score: 1.0

## Scores Produced

- Opportunity score: 0.8391
- Portfolio score: 0.8575
- Breakthrough score: 0.9440
- Viability score: 0.7722
- Buildability score: 0.7821
- Feasibility score: 0.7703
- Signal quality score: 0.3351
- Export package score: 0.9600

## Final Decision Output

- Decision: GO
- Breakthrough classification: breakthrough_candidate
- Export package level: export_ready
- Export writer status: success

## Strengths Discovered

- Climate insurance repricing and regional withdrawal were converted into a lifecycle-safe governed signal.
- The signal governance layer produced quality/relevance scoring without adding new external connectors.
- The lifecycle context captured governed signal evidence for downstream traceability.
- The export package included both `full_pipeline_output.json` and `core_lifecycle_summary.json`.

## Weaknesses And Missing Selections

- The run used a single user-supplied signal, so source diversity remains limited.
- Signal quality score remains modest at the broader pipeline score level, even though the governed signal quality score was strong.
- No screenshots were captured during this proof run.

## Completeness

Complete for v5.89.7 proof scope.

The run proves that the Signal Governance Layer can normalize, dedupe, score, accept, expose, embed, and export governed signals while preserving the core lifecycle completion gate.

## Exported Run Artifacts

- Run ID: `claire_run_20260502_100259_climate_insurance_climate_insurance_risk_intelligence`
- Export folder: `exports/claire_run_20260502_100259_climate_insurance_climate_insurance_risk_intelligence`
- Full output: `exports/claire_run_20260502_100259_climate_insurance_climate_insurance_risk_intelligence/full_pipeline_output.json`
- Lifecycle summary: `exports/claire_run_20260502_100259_climate_insurance_climate_insurance_risk_intelligence/core_lifecycle_summary.json`
