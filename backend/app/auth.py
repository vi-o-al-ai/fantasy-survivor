"""Bearer-token authentication.

Tokens are RS256 JWTs issued by Auth0. The backend never calls Auth0 on the
request path: it fetches the tenant's public keys (JWKS) once, caches them,
and verifies signatures locally. That keeps the API stateless and fast.

The verification core (``TokenVerifier``) knows nothing about HTTP or
FastAPI, so it is unit-tested with locally generated keys. The FastAPI
dependencies at the bottom adapt it to requests.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Protocol

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings

log = logging.getLogger(__name__)

ALGORITHMS = ("RS256",)


class AuthError(Exception):
    """Raised by the verifier; mapped to HTTP 401 by the dependency layer."""


@dataclass(frozen=True)
class CurrentUser:
    """What the API knows about the caller, straight from token claims."""

    sub: str
    permissions: frozenset[str] = field(default_factory=frozenset)
    scopes: frozenset[str] = field(default_factory=frozenset)
    email: str | None = None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


class KeyProvider(Protocol):
    """Resolves the public key that signed a token."""

    def signing_key_for(self, token: str) -> Any: ...


class JwksUrlKeyProvider:
    """Fetches and caches keys from a JWKS endpoint (Auth0's)."""

    def __init__(self, jwks_url: str) -> None:
        self._client = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)

    def signing_key_for(self, token: str) -> Any:
        return self._client.get_signing_key_from_jwt(token).key


class JwksFileKeyProvider:
    """Reads keys from a JWKS document on disk. Local development only."""

    def __init__(self, path: Path) -> None:
        self._key_set = jwt.PyJWKSet.from_dict(json.loads(path.read_text()))

    def signing_key_for(self, token: str) -> Any:
        kid = jwt.get_unverified_header(token).get("kid")
        if kid is None:
            raise AuthError("token has no kid header")
        try:
            return self._key_set[kid].key
        except KeyError as exc:
            raise AuthError(f"unknown signing key {kid!r}") from exc


class TokenVerifier:
    def __init__(self, *, issuer: str, audience: str, keys: KeyProvider) -> None:
        self._issuer = issuer
        self._audience = audience
        self._keys = keys

    def verify(self, token: str) -> CurrentUser:
        try:
            key = self._keys.signing_key_for(token)
            claims = jwt.decode(
                token,
                key,
                algorithms=list(ALGORITHMS),
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["exp", "iat", "sub"]},
            )
        except AuthError:
            raise
        except jwt.PyJWTError as exc:
            raise AuthError(str(exc)) from exc
        return _user_from_claims(claims)


def _user_from_claims(claims: dict[str, Any]) -> CurrentUser:
    # Auth0 puts RBAC permissions in ``permissions`` (when enabled on the API)
    # and OAuth scopes in a space-separated ``scope`` string.
    permissions = claims.get("permissions") or []
    scopes = str(claims.get("scope") or "").split()
    return CurrentUser(
        sub=str(claims["sub"]),
        permissions=frozenset(str(p) for p in permissions),
        scopes=frozenset(scopes),
        email=claims.get("email"),
    )


def build_verifier(settings: Settings) -> TokenVerifier | None:
    """Pick the key source from settings. ``None`` means auth is not configured."""
    if settings.auth_local_jwks_file is not None:
        if settings.is_deployed:
            raise RuntimeError("AUTH_LOCAL_JWKS_FILE must not be set in a deployed environment")
        log.warning(
            "auth: using LOCAL signing keys, not Auth0",
            extra={"jwks_file": str(settings.auth_local_jwks_file)},
        )
        return TokenVerifier(
            issuer=settings.auth_local_issuer,
            audience=settings.auth0_audience or "fantasy-survivor-local",
            keys=JwksFileKeyProvider(settings.auth_local_jwks_file),
        )
    if settings.auth0_domain and settings.auth0_audience:
        return TokenVerifier(
            issuer=settings.auth0_issuer,
            audience=settings.auth0_audience,
            keys=JwksUrlKeyProvider(settings.auth0_jwks_url),
        )
    if settings.is_deployed:
        raise RuntimeError("AUTH0_DOMAIN and AUTH0_AUDIENCE are required when deployed")
    log.warning("auth: not configured; protected routes will return 503")
    return None


# --- FastAPI adapters -------------------------------------------------------

_bearer = HTTPBearer(auto_error=False)


def get_token_verifier(request: Request) -> TokenVerifier:
    verifier: TokenVerifier | None = getattr(request.app.state, "token_verifier", None)
    if verifier is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="authentication is not configured"
        )
    return verifier


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> CurrentUser:
    if credentials is None:
        raise _unauthorized("missing bearer token")
    try:
        return verifier.verify(credentials.credentials)
    except AuthError as exc:
        log.info("auth: rejected token", extra={"reason": str(exc)})
        raise _unauthorized("invalid token") from exc


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_permission(permission: str) -> Callable[[CurrentUser], CurrentUser]:
    """Dependency factory: ``Depends(require_permission("write:stats"))``."""

    def _check(user: CurrentUserDep) -> CurrentUser:
        if not user.has_permission(permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"requires {permission}")
        return user

    return _check


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"}
    )
