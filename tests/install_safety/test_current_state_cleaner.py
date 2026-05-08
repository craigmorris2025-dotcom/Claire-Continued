from pathlib import Path
from claire.install_safety.current_state_cleaner import class_name_from_file, stub_content

def test_class_name_from_file():
    assert class_name_from_file(Path("technology_catalog.py")) == "TechnologyCatalog"

def test_stub_content_compilable():
    compile(stub_content("TechnologyCatalog"), "stub.py", "exec")
