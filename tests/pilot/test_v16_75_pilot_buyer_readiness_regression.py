
from pathlib import Path

from claire.pilot.pilot_offer_definition import build_pilot_offer_definition
from claire.pilot.pilot_deliverables_generator import build_pilot_deliverables_package
from claire.buyer.buyer_readiness_checklist import build_buyer_readiness_checklist
from claire.buyer.acquisition_narrative_binder import build_acquisition_narrative_binder


def test_pilot_offer_definition_builds():
    offer = build_pilot_offer_definition()
    assert offer["status"] == "defined"
    assert Path("data/pilot/governed_opportunity_intelligence_pilot.json").exists()


def test_pilot_deliverables_package_builds():
    package = build_pilot_deliverables_package()
    assert package["status"] == "ready"
    assert "go_no_go_memo" in package["deliverables"]
    assert Path("data/pilot/pilot_deliverables_package.json").exists()


def test_buyer_readiness_checklist_builds():
    checklist = build_buyer_readiness_checklist()
    assert checklist["status"] == "checklist_ready"
    assert "governance" in checklist["readiness_categories"]
    assert Path("data/buyer/buyer_readiness_checklist.json").exists()


def test_acquisition_narrative_binder_builds():
    binder = build_acquisition_narrative_binder()
    assert binder["status"] == "binder_ready"
    assert "category_thesis" in binder
    assert Path("data/buyer/acquisition_narrative_binder.json").exists()
