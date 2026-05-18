# v19.85.4–v19.85.8 Evidence Governance Batch

This pack installs five safe evidence-governance builds:

- v19.85.4 Evidence Gate Runtime Adapter
- v19.85.5 Evidence Lineage Propagation Contract
- v19.85.6 Review Queue Promotion Gate
- v19.85.7 Runtime Artifact Integrity Check
- v19.85.8 Evidence Governance Plateau Gate

## Commands

```bash
python install_claire_v19_85_4_to_v19_85_8_evidence_governance_pack.py
python tools/evidence_gate_runtime_adapter.py
python tools/evidence_lineage_propagation_contract.py
python tools/review_queue_promotion_gate.py
python tools/runtime_artifact_integrity_check.py
python tools/evidence_governance_plateau_gate.py
pytest tests/test_v19_85_4_evidence_gate_runtime_adapter.py tests/test_v19_85_5_evidence_lineage_propagation_contract.py tests/test_v19_85_6_review_queue_promotion_gate.py tests/test_v19_85_7_runtime_artifact_integrity_check.py tests/test_v19_85_8_evidence_governance_plateau_gate.py -q
```

## Plateau checks

After pytest:
- backend boot
- `/docs`
- `/dashboard/payload/status`
- `/dashboard/payload`
