from __future__ import annotations

import importlib


def test_runtime_core_is_canonical_app_namespace():
    from runtime_core.app import create_app

    app = create_app()

    assert app.title == "Governed Intelligence Platform"
    assert len(app.routes) == 353


def test_legacy_claire_app_import_path_is_retired():
    try:
        importlib.import_module("claire.app")
    except ImportError as exc:
        assert "runtime_core.app" in str(exc)
    else:
        raise AssertionError("legacy claire.app import path should fail clearly")

def test_runtime_core_can_resolve_canonical_submodules():
    module = importlib.import_module("runtime_core.api.canonical_route_manifest")

    assert hasattr(module, "CANONICAL_ROUTE_MODULES")
    assert module.__file__ is not None
    assert "\\runtime_core\\" in module.__file__
