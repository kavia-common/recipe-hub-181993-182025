from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import init_db, get_db
from .routers import recipes as recipes_router
from .routers import favorites as favorites_router
from .utils import get_allowed_origins, seed_database_if_empty

app = FastAPI(
    title="Recipe Hub API",
    description="Backend API for Recipe Hub. Provides CRUD for recipes and user favorites.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Service health checks"},
        {"name": "Recipes", "description": "Endpoints for browsing and managing recipes"},
        {"name": "Favorites", "description": "Endpoints for user favorites"},
    ],
)

# Configure CORS using env
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database schema and optionally seed demo data."""
    init_db()


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Returns a simple JSON indicating the service is healthy.",
)
def health_check(db: Session = Depends(get_db)):
    # Optionally seed DB if empty and SEED_ON_START=true
    seed_database_if_empty(db)
    return {"status": "ok"}


# Mount routers
app.include_router(recipes_router.router)
app.include_router(favorites_router.router)
