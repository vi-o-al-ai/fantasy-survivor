from scripts.export_openapi import OUTPUT, render


def test_committed_openapi_is_current() -> None:
    """docs/openapi.json is the client contract. Regenerate with scripts/export_openapi.py."""
    assert OUTPUT.exists(), f"{OUTPUT} missing; run scripts/export_openapi.py"
    assert OUTPUT.read_text() == render(), (
        "docs/openapi.json is stale; run scripts/export_openapi.py"
    )
