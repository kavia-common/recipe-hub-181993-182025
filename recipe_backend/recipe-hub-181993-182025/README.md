# Recipe Hub Workspace

This workspace contains the backend for the Recipe Hub application.

Containers:
- recipe_backend (FastAPI) – port 3001
- recipe_frontend (React) – port 3000 (lives in sibling workspace recipe-hub-181993-182024)

API docs (when backend is running): http://localhost:3001/docs

## OpenAPI schema generation

- From the repository root:
  - python -m src.api.generate_openapi
- Or from recipe_backend directory:
  - python src/api/generate_openapi.py

The schema is written to recipe_backend/interfaces/openapi.json.

## Integration notes

- Backend (FastAPI) default port: 3001
- Frontend (React) default port: 3000

Environment wiring:
- Backend CORS:
  - Always allows: http://localhost:3000 (for local dev)
  - Also allows the value provided in `FRONTEND_ORIGIN` from `recipe_backend/.env`
- Frontend API base URL:
  - Set `REACT_APP_API_URL` in the frontend `.env` (e.g., `http://localhost:3001`)
  - The frontend should read `process.env.REACT_APP_API_URL` when creating the API client

Minimal local setup:
1) Backend:
   - cd recipe_backend
   - cp .env.example .env
   - (optional) set SEED_ON_START=true
   - pip install -r requirements.txt
   - uvicorn src.api.main:app --reload --port 3001
2) Frontend:
   - cd recipe_frontend (in workspace recipe-hub-181993-182024)
   - create `.env` with: `REACT_APP_API_URL=http://localhost:3001`
   - start dev server on port 3000

Now the frontend can call the backend without CORS issues.

## Backend environment variables

See recipe_backend/.env.example for reference. Key variables:
- DB_URL: SQLAlchemy database URL. Defaults to sqlite:///./recipes.db
- FRONTEND_ORIGIN: Extra allowed CORS origin (in addition to http://localhost:3000)
- SEED_ON_START: true/false to seed demo data when DB is empty
