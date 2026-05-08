from claire.ops_closeout.freeze_manifest_builder import FreezeManifestBuilder
from claire.ops_closeout.resume_point_writer import ResumePointWriter

def test_freeze_manifest():
    assert FreezeManifestBuilder().build_manifest("11.70")["state"] == "maintenance_freeze"

def test_resume_point():
    point = ResumePointWriter().build_resume_point("11.70", ["evidence population"])
    assert point["next_focus"] == ["evidence population"]
