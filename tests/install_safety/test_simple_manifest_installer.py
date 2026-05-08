from claire.install_safety.simple_manifest_installer import parse_manifest

def test_manifest_parser_normalizes_json_booleans(tmp_path):
    installer = tmp_path / "installer.py"
    installer.write_text(
        "INSTALLER_NAME='x'\nINSTALLER_VERSION='1'\nFOLDERS=[]\nFILES={}\nVERSION_FILE='version_x.json'\nLOCK_PAYLOAD={'ok': true, 'bad': false, 'none': null}\n",
        encoding="utf-8",
    )
    manifest = parse_manifest(installer)
    assert manifest["lock_payload"]["ok"] is True
    assert manifest["lock_payload"]["bad"] is False
    assert manifest["lock_payload"]["none"] is None
