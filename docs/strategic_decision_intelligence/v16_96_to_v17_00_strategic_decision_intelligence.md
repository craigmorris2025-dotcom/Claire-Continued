# Claire v16.96-v17.00 Strategic Decision Intelligence Layer

This layer moves Claire from governed discovery toward governed strategic decisioning.

## Included Builds

- v16.96 Decision Scenario Engine
- v16.97 Bounded Outcome Simulation Layer
- v16.98 Intervention Strategy Selector
- v16.99 Expected vs Actual Outcome Tracker
- v17.00 Strategic Decision Regression Lock

## Governance Boundary

This layer recommends actions only. It does not perform external autonomous actions and does not authorize real-world execution without user approval.

## Primary Runtime

```python
from claire.strategic_decision_intelligence import StrategicDecisionRuntime

runtime = StrategicDecisionRuntime()
result = runtime.run(discovery)
```
