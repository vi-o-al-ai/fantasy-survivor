from pathlib import Path

import pytest

import scripts.mint_dev_token as mint
from app.auth import JwksFileKeyProvider, TokenVerifier


def test_mint_creates_keys_and_verifiable_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(mint, "LOCAL_DIR", tmp_path)
    monkeypatch.setattr(mint, "KEY_FILE", tmp_path / "k.pem")
    monkeypatch.setattr(mint, "JWKS_FILE", tmp_path / "jwks.json")

    token = mint.mint("dev@example.com", ["write:stats"])
    again = mint.mint("dev@example.com", [])  # reuses the key on disk

    verifier = TokenVerifier(
        issuer=mint.ISSUER, audience=mint.AUDIENCE, keys=JwksFileKeyProvider(tmp_path / "jwks.json")
    )
    user = verifier.verify(token)
    assert user.sub == "dev@example.com"
    assert user.email == "dev@example.com"
    assert user.permissions == {"write:stats"}
    assert verifier.verify(again).permissions == frozenset()
