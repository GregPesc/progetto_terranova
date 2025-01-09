from typing import Optional

from app.models import AlcoholicType, Category, Ingredient


def validate_enum_value(value: str, enum_class) -> bool:
    """Validate if a value exists in an enum class."""
    try:
        enum_class(value)
        return True  # noqa: TRY300
    except ValueError:
        return False


def validate_recipe_data(data: dict) -> tuple[bool, Optional[tuple]]:
    """Validate the incoming recipe data."""
    drink_name = data.get("name")
    category = data.get("category")
    alcoholic_type = data.get("alcoholic_type")

    if not all([drink_name, category, alcoholic_type]):
        return False, ({"error": "missing required fields"}, 400)

    if not validate_enum_value(category, Category):
        return False, (
            {
                "error": f"invalid category. Must be one of: {[e.value for e in Category]}"
            },
            400,
        )

    if not validate_enum_value(alcoholic_type, AlcoholicType):
        return False, (
            {
                "error": f"invalid alcoholic type. Must be one of: {[e.value for e in AlcoholicType]}"
            },
            400,
        )

    return True, None


def process_ingredients(
    ingredients_ids: str, ingredients_quantities: str
) -> tuple[list[Ingredient], dict[int, str | None]]:
    """Process and validate ingredients data."""
    if not ingredients_ids:
        return [], {}

    try:
        ids = [int(id_drink) for id_drink in ingredients_ids.split(",")]
        quantities = ingredients_quantities.split(",") if ingredients_quantities else []

        if len(ids) != len(quantities):
            raise ValueError("Ingredients and quantities must have the same length")  # noqa: TRY003

        # Convert empty strings to None
        quantities = [q if q.strip() else None for q in quantities]

    except ValueError as e:
        if str(e) == "Ingredients and quantities must have the same length":
            raise
        raise ValueError("Invalid ingredient IDs") from None  # noqa: TRY003

    ingredients = Ingredient.query.filter(Ingredient.id.in_(ids)).all()

    return ingredients, dict(zip(ids, quantities))
