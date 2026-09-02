"""Test-only RSA key pair and token minting. No Auth0 needed."""

from __future__ import annotations

import time
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth import KeyProvider

ISSUER = "https://test-tenant.example.com/"
AUDIENCE = "https://api.test"
KID = "test-kid"

_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()


class StaticKeyProvider:
    """Returns the test public key regardless of token. Optionally the wrong one."""

    def __init__(self, key: Any = _PUBLIC_KEY) -> None:
        self._key = key

    def signing_key_for(self, token: str) -> Any:
        return self._key


def key_provider() -> KeyProvider:
    return StaticKeyProvider()


def mint_token(
    *,
    sub: str = "auth0|user123",
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
    permissions: list[str] | None = None,
    scope: str = "",
    email: str | None = None,
    ttl: int = 300,
    private_key: Any = None,
    **extra: Any,
) -> str:
    now = int(time.time())
    claims: dict[str, Any] = {
        "iss": issuer,
        "aud": audience,
        "sub": sub,
        "iat": now,
        "exp": now + ttl,
        **extra,
    }
    if permissions is not None:
        claims["permissions"] = permissions
    if scope:
        claims["scope"] = scope
    if email:
        claims["email"] = email
    return jwt.encode(claims, private_key or _PRIVATE_KEY, algorithm="RS256", headers={"kid": KID})
