# Recipe Hub Backend (FastAPI)

Backend API for Recipe Hub. Provides CRUD for recipes and user favorites.

- API Docs (running container): http://localhost:3001/docs
- OpenAPI schema generation:
  - From the repository root:
    - python -m src.api.generate_openapi
  - Or from recipe_backend directory:
    - python src/api/generate_openapi.py

The schema is written to recipe_backend/interfaces/openapi.json.

## Environment variables

Create a `.env` file in `recipe_backend/` to configure the service. Do not commit secrets.

Example `.env.example`:

```
# Database configuration
# Defaults to a local sqlite file if not provided
DB_URL=sqlite:///./recipes.db

# CORS configuration
# The frontend origin to allow. Default is http://localhost:3000
FRONTEND_ORIGIN=http://localhost:3000

# Seed data on startup (true/false). Default: false
SEED_ON_START=true
```

Notes:
- CORS: The app always allows `http://localhost:3000` by default for local dev and additionally any `FRONTEND_ORIGIN` value you provide.
- DB: If you use SQLite, the DB file `recipes.db` will be created at the backend project root.

## Ports

- Backend default dev server port: 3001
  - Example: uvicorn src.api.main:app --reload --port 3001
- Frontend default dev server port: 3000

Ensure the frontend points to the backend using `REACT_APP_API_URL=http://localhost:3001`.

## Running locally

1) Create and activate virtual environment (optional).
2) Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3) Configure `.env` as above.
4) Start the backend:
   ```
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
   ```
5) Visit:
   - Health: http://localhost:3001/health
   - Docs: http://localhost:3001/docs

## Frontend integration

In the frontend (React), configure the API base URL using environment variables:

- Create `.env` in the frontend project (recipe_frontend):
  ```
  REACT_APP_API_URL=http://localhost:3001
  ```
- Your API client should read from `process.env.REACT_APP_API_URL`, for example:
  ```js
  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  ```

CORS is enabled on the backend for `http://localhost:3000` by default and any `FRONTEND_ORIGIN` set in the backend `.env`.

## Seeding

If `SEED_ON_START=true`, a couple of demo recipes will be automatically inserted when `/health` is first called or on app start when DB is empty.

## Production notes

- Set `FRONTEND_ORIGIN` to the deployed frontend URL (e.g., `https://app.example.com`).
- Set `DB_URL` to your production database connection string.
- Ensure `REACT_APP_API_URL` on the frontend is set to your deployed backend URL.
