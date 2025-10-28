import os
from typing import Optional, Tuple, Sequence, Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from . import models

# Load .env if present
load_dotenv()

DEFAULT_FRONTEND_ORIGIN = "http://localhost:3000"
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


# PUBLIC_INTERFACE
def get_allowed_origins() -> list[str]:
    """Return list of allowed CORS origins using FRONTEND_ORIGIN env and localhost default."""
    origins = [DEFAULT_FRONTEND_ORIGIN]
    env_origin = os.getenv("FRONTEND_ORIGIN")
    if env_origin:
        origins.append(env_origin)
    return list(dict.fromkeys(origins))  # de-duplicate


# PUBLIC_INTERFACE
def get_seed_flag() -> bool:
    """Return True if SEED_ON_START is set to 'true' (case-insensitive)."""
    return os.getenv("SEED_ON_START", "false").lower() == "true"


# PUBLIC_INTERFACE
def get_user_id_from_headers(x_user_id: Optional[str]) -> str:
    """Extract user ID from header value, raising ValueError if missing."""
    if not x_user_id:
        raise ValueError("Missing X-User-Id header")
    return x_user_id


# PUBLIC_INTERFACE
def parse_tags_to_string(tags: Optional[list[str]]) -> Optional[str]:
    """Convert list of tags to comma-separated string, trimming whitespace."""
    if tags is None:
        return None
    return ",".join(sorted({t.strip() for t in tags if t and t.strip()}))


# PUBLIC_INTERFACE
def parse_tags_to_list(tags_str: Optional[str]) -> Optional[list[str]]:
    """Convert a comma-separated tags string to a list."""
    if not tags_str:
        return None
    return [t for t in (tag.strip() for tag in tags_str.split(",")) if t]


# PUBLIC_INTERFACE
def seed_database_if_empty(db: Session) -> None:
    """Seed database with a few recipes if empty and SEED_ON_START is true."""
    if not get_seed_flag():
        return
    count = db.scalar(select(func.count()).select_from(models.Recipe)) or 0
    if count > 0:
        return
    demo_recipes = [
        models.Recipe(
            title="Classic Margherita Pizza",
            description="Simple pizza with tomato, mozzarella, and basil.",
            ingredients="- Pizza dough\n- Tomato sauce\n- Fresh mozzarella\n- Basil\n- Olive oil\n- Salt",
            instructions="1. Preheat oven to 500F.\n2. Spread sauce on dough.\n3. Add mozzarella and basil.\n4. Bake 8-10 min.",
            cuisine="Italian",
            tags="pizza,vegetarian,quick",
            author_id="seed",
        ),
        models.Recipe(
            title="Chana Masala",
            description="Spiced chickpea curry.",
            ingredients="- Chickpeas\n- Onion\n- Tomato\n- Spices\n- Garlic\n- Ginger",
            instructions="Saute aromatics, add spices, tomatoes, chickpeas, simmer.",
            cuisine="Indian",
            tags="vegan,gluten-free,curry",
            author_id="seed",
        ),
    ]
    db.add_all(demo_recipes)
    db.commit()


# PUBLIC_INTERFACE
def apply_pagination(query, page: int, page_size: int) -> Tuple[int, Sequence[Any]]:
    """Return total count and paginated results for a SQLAlchemy select query."""
    # total count
    total = query.session.scalar(select(func.count()).select_from(query.subquery()))
    # page results
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return int(total or 0), items
