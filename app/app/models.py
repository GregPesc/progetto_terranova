from __future__ import annotations

import enum

from flask_login import UserMixin
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db, login_manager


class ApiDrink(db.Model):
    __tablename__ = "ApiDrink"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<ApiDrink id={self.id}, name={self.name}, thumbnail={self.thumbnail}>"


class AlcoholicType(enum.Enum):
    ALCOHOLIC = "Alcoholic"
    NON_ALCOHOLIC = "Non alcoholic"
    OPTIONAL_ALCOHOL = "Optional alcohol"


class Category(enum.Enum):
    COCKTAIL = "Cocktail"
    ORDINARY_DRINK = "Ordinary Drink"
    PUNCH_PARTY_DRINK = "Punch / Party Drink"
    SHAKE = "Shake"
    OTHER_UNKNOWN = "Other / Unknown"
    COCOA = "Cocoa"
    SHOT = "Shot"
    COFFEE_TEA = "Coffee / Tea"
    HOMEMADE_LIQUEUR = "Homemade Liqueur"
    BEER = "Beer"
    SOFT_DRINK = "Soft Drink"


# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#setting-bi-directional-many-to-many
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table

drink_ingredient = db.Table(
    "drink_ingredient_association",
    db.Model.metadata,
    Column("drink_id", ForeignKey("UserDrink.id"), primary_key=True),
    Column("measure", String, nullable=True),
    Column("ingredients_id", ForeignKey("Ingredient.id"), primary_key=True),
)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#configuring-delete-behavior-for-one-to-many
class User(db.Model, UserMixin):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[int] = mapped_column(nullable=False)
    user_drinks: Mapped[list[UserDrink]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_favorites: Mapped[list[Favorite]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_custom_ingredients: Mapped[list[Ingredient]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User id={self.id}, email={self.email}, password={self.password}"


class UserDrink(db.Model):
    __tablename__ = "UserDrink"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[Category] = mapped_column(nullable=False)
    alcoholic_type: Mapped[AlcoholicType] = mapped_column(nullable=False)
    instructions: Mapped[str] = mapped_column(nullable=True)
    thumbnail: Mapped[str] = mapped_column(nullable=True)
    ingredients: Mapped[list[Ingredient]] = relationship(
        secondary=drink_ingredient, back_populates="drinks"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="user_drinks")

    def __repr__(self):
        return f"<UserDrink id={self.id}, name={self.name}, category={self.category}, alcoholic_type={self.alcoholic_type}, instructions={self.instructions}, thumbnail={self.thumbnail}, ingredients={self.ingredients}>"


class Ingredient(db.Model):
    __tablename__ = "Ingredient"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    drinks: Mapped[list[UserDrink]] = relationship(
        secondary=drink_ingredient, back_populates="ingredients"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=True)
    user: Mapped[User] = relationship(back_populates="user_custom_ingredients")

    def __repr__(self):
        return f"<Ingredient id={self.id}, name={self.name}, drinks={self.drinks}, user_id={self.user_id}>"


class Favorite(db.Model):
    __tablename__ = "Favorite"

    drink_id: Mapped[int] = mapped_column(primary_key=True)
    is_local: Mapped[bool] = mapped_column(
        Boolean(create_constraint=True), nullable=False, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="user_favorites")

    def __repr__(self):
        return f"<Favorite drink_id={self.drink_id}, is_local={self.is_local}, user_id={self.user_id}>"
