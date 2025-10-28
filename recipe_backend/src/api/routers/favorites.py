from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..utils import get_user_id_from_headers

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.get(
    "",
    response_model=list[schemas.FavoriteOut],
    summary="List favorites",
    description="Get current user's favorite recipes. Requires X-User-Id header.",
)
def list_favorites(
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    stmt = select(models.Favorite).where(models.Favorite.user_id == user_id).order_by(models.Favorite.created_at.desc())
    rows: List[models.Favorite] = db.execute(stmt).scalars().all()
    return [schemas.FavoriteOut.model_validate(r) for r in rows]


@router.post(
    "",
    response_model=schemas.FavoriteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add favorite",
    description="Add a recipe to current user's favorites. Requires X-User-Id header.",
)
def add_favorite(
    payload: schemas.FavoriteCreate,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    recipe = db.get(models.Recipe, payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    favorite = models.Favorite(user_id=user_id, recipe_id=payload.recipe_id)
    db.add(favorite)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already favorited")
    db.refresh(favorite)
    return schemas.FavoriteOut.model_validate(favorite)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove favorite",
    description="Remove a recipe from current user's favorites via body payload. Requires X-User-Id header.",
)
def remove_favorite_by_body(
    payload: schemas.FavoriteCreate,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    stmt = select(models.Favorite).where(
        models.Favorite.user_id == user_id,
        models.Favorite.recipe_id == payload.recipe_id,
    )
    fav = db.execute(stmt).scalars().first()
    if not fav:
        # Idempotent delete: 204 even if not present
        return
    db.delete(fav)
    db.commit()
    return


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove favorite by recipe ID",
    description="Remove a recipe from current user's favorites via path parameter. Requires X-User-Id header.",
)
def remove_favorite_by_path(
    recipe_id: int,
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    try:
        user_id = get_user_id_from_headers(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Missing X-User-Id")

    stmt = select(models.Favorite).where(
        models.Favorite.user_id == user_id,
        models.Favorite.recipe_id == recipe_id,
    )
    fav = db.execute(stmt).scalars().first()
    if not fav:
        return
    db.delete(fav)
    db.commit()
    return
