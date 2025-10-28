from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base


class Recipe(Base):
    """Recipe entity representing a user-submitted recipe."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    cuisine: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)  # comma-separated list
    author_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="recipe", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_recipes_title_cuisine", "title", "cuisine"),
    )


class Favorite(Base):
    """Favorite mapping between user and recipe IDs."""
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )
