from claire.operational_proof.operational_proof_plateau import OperationalProofPlateau

def test_plateau_manifest():
    manifest = OperationalProofPlateau().build_manifest()
    assert manifest["version"] == "11.50"
