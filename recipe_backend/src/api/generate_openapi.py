#!/usr/bin/env python3
"""
Utility to generate and export the FastAPI OpenAPI schema.

This script:
- Imports the FastAPI app from src.api.main
- Calls app.openapi() to get the schema
- Ensures the 'interfaces' directory exists under recipe_backend
- Writes the schema to recipe_backend/interfaces/openapi.json

Run from the repository root or the recipe_backend directory:
    python -m src.api.generate_openapi
or:
    python src/api/generate_openapi.py
"""
import json
import sys
from pathlib import Path

# Allow running the script directly by ensuring project root is in path
# Compute base as the recipe_backend directory (two levels up from this file)
CURRENT_FILE = Path(__file__).resolve()
RECIPE_BACKEND_DIR = CURRENT_FILE.parents[2]  # .../recipe_backend
REPO_ROOT = RECIPE_BACKEND_DIR.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import app after sys.path adjustment
from src.api.main import app  # noqa: E402


def _resolve_output_path() -> Path:
    """
    Resolve the output path for interfaces/openapi.json relative to recipe_backend.
    This ensures consistent output regardless of the invocation working directory.
    """
    interfaces_dir = RECIPE_BACKEND_DIR / "interfaces"
    interfaces_dir.mkdir(parents=True, exist_ok=True)
    return interfaces_dir / "openapi.json"


def main() -> int:
    """
    Generate the OpenAPI schema and write it to interfaces/openapi.json.
    Returns process exit code: 0 on success, non-zero on failure.
    """
    try:
        schema = app.openapi()
    except Exception as exc:
        print(f"Failed to build OpenAPI schema: {exc}", file=sys.stderr)
        return 1

    output_path = _resolve_output_path()
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
        # Provide a small confirmation for CI logs
        print(f"Wrote OpenAPI schema to: {output_path}")
    except Exception as exc:
        print(f"Failed to write OpenAPI schema: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
