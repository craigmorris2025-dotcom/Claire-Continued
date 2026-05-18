# v19.85.1 Evidence Basket Contract

This build defines the canonical evidence basket schema.

It formalizes:
- evidence lineage,
- source attribution,
- confidence ownership,
- validation rules,
- invalid evidence conditions.

## Commands

```bash
python tools/evidence_basket_contract.py
pytest tests/test_v19_85_1_evidence_basket_contract.py -q
```

## Output

- `data/evidence_governance/evidence_basket_contract.json`
- `audits/v19_85_1_evidence_basket_contract/evidence_basket_contract.json`
- `audits/v19_85_1_evidence_basket_contract/evidence_basket_contract.md`

## Locked Principle

No evidence promotion without lineage.
