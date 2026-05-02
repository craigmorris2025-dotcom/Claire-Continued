# Master Plan Alignment

Governing reference:

- `C:/Users/craig/OneDrive/Documents/Claire_Master_System_Build_Plan_v5_89_5_to_v5_99.docx`

## Intended Architecture

The master plan defines Claire as a governed recursive engine:

External signals / market data / company data / sector data / existing portfolios / prior Claire outputs / existing systems
-> Signal Governance
-> Trend Discovery
-> Thesis Formation
-> Portfolio Creation / Optimization
-> Breakthrough Escalation Gate
-> Breakthrough Classification
-> Advancement Path Selection
-> Correct Route
-> Lifecycle Memory
-> Recursive Self-Ingestion
-> Stronger Future Runs

The repo currently has a working backend pipeline, dashboard/export surfaces, launchers, regression tests, and a legacy 21-stage lifecycle evaluator. The alignment move for v5.89.5 is to add the canonical 30-stage lifecycle as a stable spine without breaking the existing app.

## Intended Lifecycle

The canonical master-plan lifecycle has 30 stages:

1. Signal Ingestion
2. Signal Normalization
3. Source Validation & Weighting
4. Context Expansion
5. Signal Consolidation
6. Entity Extraction
7. Relationship Mapping
8. Trend Discovery
9. Cluster Formation
10. Insight / Thesis Structuring
11. Gap Detection
12. Gap Qualification
13. Discovery Generation
14. Breakthrough Identification & Classification
15. Advancement Path Selection
16. Auto Invention / Solution Generation
17. Solution Structuring
18. Buildability Assessment
19. Viability Assessment
20. Manufacturability / Deployability Assessment
21. Feasibility Validation
22. Design Portal Output / Blueprints / Specs
23. Market Positioning
24. Moat & Differentiation
25. Business Model & Value Capture
26. Competitor Analysis
27. Portfolio Creation / Optimization
28. Acquirer Identification
29. Acquisition Fit & Rationale
30. Final Package Construction

## Version Alignment

Current target confirmed:

- v5.89.5 is the current next target: Trend Discovery Backbone + Lifecycle Spine.
- v5.89.6 may follow only after v5.89.5 remains stable: Stage Contract Enforcement.

Current implementation alignment:

- v5.89.5: Implemented as canonical 30-stage registry, unified context, allowed statuses, run summary, and pipeline-visible `core_lifecycle`.
- v5.89.6: Implemented lightly as stage contracts, route-dependent rules, validator, and completion gate.
- v5.89.7+: Deferred. Signal governance and trend/thesis expansion should not be started in this run.

## Preservation Rules

- Preserve current backend launchers.
- Preserve dashboard Evaluate / Discover / Monitor mode behavior.
- Preserve existing endpoints.
- Preserve legacy 21-stage lifecycle fields until downstream consumers migrate.
- Do not redesign UI.
- Do not build v5.90+ breakthrough escalation or v5.99 memory in this run.
