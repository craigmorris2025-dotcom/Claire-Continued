# v19.86.0–v19.86.4 Source Universe Evidence Lineage Pack

Installs:
- v19.86.0 Source Universe Evidence Lineage
- v19.86.1 Source Probe Result Schema
- v19.86.2 Probe-to-Evidence Basket Builder
- v19.86.3 Source Trust and Rejection Reasons
- v19.86.4 Source Universe Evidence Plateau Gate

## Commands

```bash
python install_claire_v19_86_0_to_v19_86_4_source_universe_evidence_pack.py
python tools/source_universe_evidence_lineage.py
python tools/source_probe_result_schema.py
python tools/probe_to_evidence_basket_builder.py
python tools/source_trust_rejection_reasons.py
python tools/source_universe_evidence_plateau_gate.py
pytest tests/test_v19_86_0_source_universe_evidence_lineage.py tests/test_v19_86_1_source_probe_result_schema.py tests/test_v19_86_2_probe_to_evidence_basket_builder.py tests/test_v19_86_3_source_trust_rejection_reasons.py tests/test_v19_86_4_source_universe_evidence_plateau_gate.py -q
```
