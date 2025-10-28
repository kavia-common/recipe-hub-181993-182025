from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    title: str = Field(..., description="Title of the recipe", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Short description for the recipe")
    ingredients: str = Field(..., description="Ingredients as text or list in text form")
    instructions: str = Field(..., description="Cooking steps/instructions")
    cuisine: Optional[str] = Field(None, description="Cuisine type, e.g., Italian, Indian")
    tags: Optional[List[str]] = Field(None, description="List of tags for the recipe")

    # Convert list of tags to comma-separated string in model usage will be handled in router


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    ingredients: Optional[str] = Field(None, description="Updated ingredients")
    instructions: Optional[str] = Field(None, description="Updated instructions")
    cuisine: Optional[str] = Field(None, description="Updated cuisine")
    tags: Optional[List[str]] = Field(None, description="Updated list of tags")


class RecipeOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    ingredients: str
    instructions: str
    cuisine: Optional[str]
    tags: Optional[List[str]]
    author_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedRecipes(BaseModel):
    total: int = Field(..., description="Total count of items matching filters")
    page: int = Field(..., description="Current page number (1-based)")
    page_size: int = Field(..., description="Number of items per page")
    items: List[RecipeOut] = Field(..., description="List of recipes for this page")


class FavoriteCreate(BaseModel):
    recipe_id: int = Field(..., description="ID of the recipe to favorite")


class FavoriteOut(BaseModel):
    id: int
    user_id: str
    recipe_id: int
    created_at: datetime

    class Config:
        from_attributes = True
