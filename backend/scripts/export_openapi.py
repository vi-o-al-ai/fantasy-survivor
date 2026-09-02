"""Write the OpenAPI spec to docs/openapi.json (the client contract).

Run after changing any route: ``python scripts/export_openapi.py``.
A test fails if the committed file is stale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.config import Settings
from app.main import create_app

OUTPUT = Path(__file__).resolve().parent.parent.parent / "docs" / "openapi.json"


def render() -> str:
    app = create_app(Settings(app_env="test", log_format="console", log_level="WARNING"))
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    OUTPUT.write_text(render())
    sys.stdout.write(f"wrote {OUTPUT}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
