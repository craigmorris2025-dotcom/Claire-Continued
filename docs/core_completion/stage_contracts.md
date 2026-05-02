# Stage Contracts

Stage contracts live in:

- `src/claire/lifecycle/stage_contracts.py`
- `src/claire/lifecycle/contract_validator.py`
- `src/claire/lifecycle/completion_gate.py`

Each stage declares required output keys and whether it is required, optional, or route-dependent.

Route-dependent stages:

- Auto Invention / Solution Generation
- Solution Structuring
- Buildability Assessment
- Manufacturability / Deployability Assessment
- Feasibility Validation
- Design Portal Output / Blueprints / Specs

Portfolio-only runs may skip route-dependent invention/design stages. Breakthrough/design runs require the design and validation outputs implied by that route.

The final completion gate reports `complete`, `incomplete`, `blocked`, `insufficient_data`, or `skipped_by_route` state without claiming package completion unless required route outputs exist.
