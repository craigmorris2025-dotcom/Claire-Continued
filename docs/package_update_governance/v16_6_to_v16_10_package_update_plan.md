# v16.6-v16.10 Internet Package Update Governance

Recommended modern package approach:

1. Keep direct dependency intent in `requirements/*.in`.
2. Compile pinned requirements with `pip-compile`.
3. Audit with `pip-audit`.
4. Run targeted and full pytest.
5. Commit only after launcher/dashboard proof.

Manual commands:

```bat
python -m pip install pip-tools pip-audit
pip-compile requirements/live_connectivity.in -o requirements/live_connectivity.txt
python -m pip install -r requirements/live_connectivity.txt
python -m pip_audit
pytest
```
