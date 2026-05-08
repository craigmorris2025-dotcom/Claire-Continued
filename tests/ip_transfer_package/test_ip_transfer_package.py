from claire.ip_transfer_package.transfer_checklist import TransferChecklist
from claire.ip_transfer_package.ownership_record_builder import OwnershipRecordBuilder

def test_transfer_checklist_incomplete():
    assert TransferChecklist().evaluate({})["status"] == "incomplete"

def test_ownership_record():
    assert OwnershipRecordBuilder().build_record()["owner"] == "Craig Morris"
