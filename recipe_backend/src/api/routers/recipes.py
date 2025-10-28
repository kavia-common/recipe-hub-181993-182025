from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..utils import parse_tags_to_string, parse_tags_to_list, get_user_id_from_headers, MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


@router.get(
    "",
    response_model=schemas.PaginatedRecipes,
    summary="List recipes",
    description="List recipes with pagination and optional search filters. Supports 'q' text search across title and description, 'cuisine' exact match, and 'tag' contains within comma-separated tags.",
)
def list_recipes(
    q: Optional[str] = Query(None, description="Search text across title and description"),
    cuisine: Optional[str] = Query(None, description="Cuisine exact match"),
    tag: Optional[str] = Query(None, description="Tag to match within tags list"),
    page: int = Query(1, ge=1, description="1-based page index"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description=f"Items per page (max {MAX_PAGE_SIZE})"),
    db: Session = Depends(get_db),
):
    stmt = select(models.Recipe)
    filters = []
    if q:
        like = f"%{q}%"
        filters.append(or_(models.Recipe.title.ilike(like), models.Recipe.description.ilike(like)))
    if cuisine:
        filters.append(models.Recipe.cuisine == cuisine)
    if tag:
        like_tag = f"%{tag}%"
        filters.append(models.Recipe.tags.ilike(like_tag))
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(models.Recipe.created_at.desc())

    total = db.scalar(select(models.Recipe).with_only_columns(models.Recipe.id).where(and_(*filters)) if filters else select(models.Recipe).with_only_columns(models.Recipe.id))
    # Efficient total count
    if filters:
        total = db.scalar(select(models.Recipe).where(and_(*filters)).with_only_columns(models.Recipe.id).count())  # type: ignore[attr-defined]
    # Fallback generic count via subquery
    sub = stmt.subquery()
    total = db.scalar(select().with_only_columns([db.query(sub).count()])) if False else db.query(sub).count()  # type: ignore

    offset = (page - 1) * page_size
    rows: List[models.Recipe] = db.execute(stmt.offset(offset).limit(page_size)).scalars().all()

    items = []
    for r in rows:
        items.append(
            schemas.RecipeOut(
                id=r.id,
                title=r.title,
                description=r.description,
                ingredients=r.ingredients,
                instructions=r.instructions,
                cuisine=r.cuisine,
                tags=parse_tags_to_list(r.tags),
                author_id=r.author_id,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return schemas.PaginatedRecipes(total=total, page=page, page_size=page_size, items=items)


@router.post(
    "",
    response_model=schemas.RecipeOut,
    status_code=201,
    summary="Create a recipe",
    description="Create a new recipe. Requires X-User-Id header to set author.",
)
def create_recipe(
    payload: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    tags_str = parse_tags_to_string(payload.tags)
    recipe = models.Recipe(
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        cuisine=payload.cuisine,
        tags=tags_str,
        author_id=user_id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return schemas.RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        cuisine=recipe.cuisine,
        tags=parse_tags_to_list(recipe.tags),
        author_id=recipe.author_id,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.get(
    "/{recipe_id}",
    response_model=schemas.RecipeOut,
    summary="Get recipe by ID",
    description="Retrieve a recipe details by its ID.",
)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return schemas.RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        cuisine=recipe.cuisine,
        tags=parse_tags_to_list(recipe.tags),
        author_id=recipe.author_id,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.put(
    "/{recipe_id}",
    response_model=schemas.RecipeOut,
    summary="Update recipe",
    description="Update a recipe. Only the author can update; requires X-User-Id header.",
)
def update_recipe(
    recipe_id: int,
    payload: schemas.RecipeUpdate,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    recipe = db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.author_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: not the author")

    # Apply updates if provided
    if payload.title is not None:
        recipe.title = payload.title
    if payload.description is not None:
        recipe.description = payload.description
    if payload.ingredients is not None:
        recipe.ingredients = payload.ingredients
    if payload.instructions is not None:
        recipe.instructions = payload.instructions
    if payload.cuisine is not None:
        recipe.cuisine = payload.cuisine
    if payload.tags is not None:
        recipe.tags = parse_tags_to_string(payload.tags)

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return schemas.RecipeOut(
        id=recipe.id,
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        cuisine=recipe.cuisine,
        tags=parse_tags_to_list(recipe.tags),
        author_id=recipe.author_id,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.delete(
    "/{recipe_id}",
    status_code=204,
    summary="Delete recipe",
    description="Delete a recipe by ID. Only the author can delete; requires X-User-Id header.",
)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    recipe = db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.author_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: not the author")

    db.delete(recipe)
    db.commit()
    return
