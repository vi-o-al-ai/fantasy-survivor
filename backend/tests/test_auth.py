import json
from pathlib import Path
from typing import Annotated

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.auth import AuthError, JwksFileKeyProvider, TokenVerifier, build_verifier
from app.config import Settings
from tests import auth_keys
from tests.auth_keys import StaticKeyProvider, mint_token

# --- TokenVerifier (pure) ---------------------------------------------------


def test_valid_token_yields_user(verifier: TokenVerifier) -> None:
    token = mint_token(
        sub="auth0|abc",
        permissions=["read:stats", "write:stats"],
        scope="openid profile",
        email="abc@example.com",
    )

    user = verifier.verify(token)

    assert user.sub == "auth0|abc"
    assert user.permissions == {"read:stats", "write:stats"}
    assert user.scopes == {"openid", "profile"}
    assert user.email == "abc@example.com"
    assert user.has_permission("write:stats")
    assert not user.has_permission("admin")


@pytest.mark.parametrize(
    "bad",
    [
        {"audience": "https://someone-else"},
        {"issuer": "https://evil.example.com/"},
        {"ttl": -10},
    ],
    ids=["wrong-audience", "wrong-issuer", "expired"],
)
def test_bad_claims_rejected(verifier: TokenVerifier, bad: dict[str, object]) -> None:
    with pytest.raises(AuthError):
        verifier.verify(mint_token(**bad))  # type: ignore[arg-type]


def test_wrong_signing_key_rejected(verifier: TokenVerifier) -> None:
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(AuthError):
        verifier.verify(mint_token(private_key=other))


def test_garbage_token_rejected(verifier: TokenVerifier) -> None:
    with pytest.raises(AuthError):
        verifier.verify("not.a.jwt")


def test_alg_none_rejected() -> None:
    # A token claiming alg=none must never be accepted even if the key lookup succeeds.
    import jwt

    claims = {"sub": "x", "iss": auth_keys.ISSUER, "aud": auth_keys.AUDIENCE}
    token = jwt.encode(claims, key="", algorithm="none")
    verifier = TokenVerifier(
        issuer=auth_keys.ISSUER, audience=auth_keys.AUDIENCE, keys=StaticKeyProvider()
    )
    with pytest.raises(AuthError):
        verifier.verify(token)


# --- HTTP layer -------------------------------------------------------------


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get("/me", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid token"}


def test_me_returns_claims(client: TestClient) -> None:
    token = mint_token(sub="auth0|me", permissions=["read:stats"], email="me@example.com")

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "sub": "auth0|me",
        "email": "me@example.com",
        "permissions": ["read:stats"],
    }


def test_protected_route_503_when_auth_unconfigured(settings: Settings) -> None:
    from app.main import create_app

    app = create_app(settings)  # no verifier override, no auth settings
    with TestClient(app) as c:
        response = c.get("/me", headers={"Authorization": "Bearer x"})

    assert response.status_code == 503


# --- build_verifier / settings wiring --------------------------------------


def _write_jwks(path: Path) -> None:
    import base64

    numbers = auth_keys._PUBLIC_KEY.public_numbers()

    def b64(n: int, length: int) -> str:
        return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

    path.write_text(
        json.dumps(
            {
                "keys": [
                    {
                        "kty": "RSA",
                        "use": "sig",
                        "alg": "RS256",
                        "kid": auth_keys.KID,
                        "n": b64(numbers.n, 256),
                        "e": b64(numbers.e, 3),
                    }
                ]
            }
        )
    )


def test_local_jwks_file_verifier(tmp_path: Path) -> None:
    jwks = tmp_path / "jwks.json"
    _write_jwks(jwks)
    settings = Settings(
        app_env="local",
        auth_local_jwks_file=jwks,
        auth_local_issuer=auth_keys.ISSUER,
        auth0_audience=auth_keys.AUDIENCE,
    )

    verifier = build_verifier(settings)

    assert verifier is not None
    assert verifier.verify(mint_token(sub="local|1")).sub == "local|1"


def test_local_jwks_unknown_kid_rejected(tmp_path: Path) -> None:
    jwks = tmp_path / "jwks.json"
    _write_jwks(jwks)
    provider = JwksFileKeyProvider(jwks)
    import jwt

    token = jwt.encode(
        {"sub": "x"}, auth_keys._PRIVATE_KEY, algorithm="RS256", headers={"kid": "other"}
    )

    with pytest.raises(AuthError, match="unknown signing key"):
        provider.signing_key_for(token)


def test_local_jwks_refused_when_deployed(tmp_path: Path) -> None:
    settings = Settings(app_env="dev", auth_local_jwks_file=tmp_path / "jwks.json")

    with pytest.raises(RuntimeError, match="deployed"):
        build_verifier(settings)


def test_deployed_requires_auth0(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="AUTH0_DOMAIN"):
        build_verifier(Settings(app_env="prod"))


def test_auth0_settings_build_url_provider() -> None:
    settings = Settings(
        app_env="local", auth0_domain="t.us.auth0.com", auth0_audience="https://api"
    )

    assert settings.auth0_issuer == "https://t.us.auth0.com/"
    assert settings.auth0_jwks_url == "https://t.us.auth0.com/.well-known/jwks.json"
    assert build_verifier(settings) is not None


def test_unconfigured_local_is_none() -> None:
    assert build_verifier(Settings(app_env="local")) is None


# --- require_permission -----------------------------------------------------


@pytest.fixture
def guarded_client(client: TestClient) -> TestClient:
    from fastapi import Depends, FastAPI

    from app.auth import CurrentUser, require_permission

    def guarded(
        user: Annotated[CurrentUser, Depends(require_permission("write:stats"))],
    ) -> dict[str, str]:
        return {"sub": user.sub}

    app = client.app
    assert isinstance(app, FastAPI)
    app.add_api_route("/guarded", guarded, methods=["GET"])
    return client


def test_permission_granted(guarded_client: TestClient) -> None:
    token = mint_token(permissions=["write:stats"])

    response = guarded_client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


def test_permission_denied(guarded_client: TestClient) -> None:
    token = mint_token(permissions=["read:stats"])

    response = guarded_client.get("/guarded", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json() == {"detail": "requires write:stats"}
