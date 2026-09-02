"""Identifier generation for user-created entities."""

from __future__ import annotations

import re
import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits
_NON_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_length: int = 24) -> str:
    slug = _NON_SLUG.sub("-", text.lower()).strip("-")[:max_length].strip("-")
    return slug or "league"


def new_league_id(name: str) -> str:
    """Readable and unique enough: ``<slug>-<6 hex>``."""
    return f"{slugify(name)}-{secrets.token_hex(3)}"


def new_join_code(length: int = 8) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
