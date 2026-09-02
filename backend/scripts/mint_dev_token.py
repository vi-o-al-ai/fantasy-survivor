"""Mint a locally signed access token for API-only development.

Creates an RSA key pair and JWKS under ``backend/.local/`` on first run, then
prints a token. Point the API at the JWKS with::

    AUTH_LOCAL_JWKS_FILE=.local/dev-jwks.json

Usage::

    python scripts/mint_dev_token.py [--sub user@example.com] [--permission write:stats ...]
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

LOCAL_DIR = Path(__file__).resolve().parent.parent / ".local"
KEY_FILE = LOCAL_DIR / "dev-key.pem"
JWKS_FILE = LOCAL_DIR / "dev-jwks.json"
KID = "local-dev"
ISSUER = "http://localhost/dev-issuer/"
AUDIENCE = "fantasy-survivor-local"


def _b64url(n: int, length: int) -> str:
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()


def ensure_keys() -> rsa.RSAPrivateKey:
    LOCAL_DIR.mkdir(exist_ok=True)
    if KEY_FILE.exists():
        loaded = serialization.load_pem_private_key(KEY_FILE.read_bytes(), password=None)
        if not isinstance(loaded, rsa.RSAPrivateKey):  # pragma: no cover - defensive
            raise SystemExit(f"{KEY_FILE} is not an RSA key")
        return loaded
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    KEY_FILE.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    numbers = key.public_key().public_numbers()
    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": KID,
                "n": _b64url(numbers.n, 256),
                "e": _b64url(numbers.e, 3),
            }
        ]
    }
    JWKS_FILE.write_text(json.dumps(jwks, indent=2))
    return key


def mint(sub: str, permissions: list[str], ttl_seconds: int = 8 * 3600) -> str:
    key = ensure_keys()
    now = int(time.time())
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": sub,
        "iat": now,
        "exp": now + ttl_seconds,
        "permissions": permissions,
        "email": sub if "@" in sub else None,
    }
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": KID})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sub", default="dev-user@example.com")
    parser.add_argument("--permission", action="append", default=[], dest="permissions")
    args = parser.parse_args(argv)
    sys.stdout.write(mint(args.sub, args.permissions) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
