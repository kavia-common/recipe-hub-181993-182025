# recipe-hub-181993-182025

OpenAPI schema generation:
- From the repository root:
  - python -m src.api.generate_openapi
- Or from recipe_backend directory:
  - python src/api/generate_openapi.py

The schema is written to recipe_backend/interfaces/openapi.json.