from claire.operational_proof.governance_deployment_lock import GovernanceDeploymentLock

def test_governance_lock():
    lock = GovernanceDeploymentLock().build_lock("11.49")
    assert lock["controls"]["live_activation_gated"] is True
