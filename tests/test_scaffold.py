import importlib

PACKAGES = ["ingest", "engine", "engine.invariants", "retrieval", "answer", "api", "ui", "eval"]


def test_packages_importable():
    for name in PACKAGES:
        importlib.import_module(name)
