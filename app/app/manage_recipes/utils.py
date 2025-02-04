import enum

from werkzeug.datastructures import ImmutableMultiDict

from app import db
from app.models import AlcoholicType, Category, Ingredient


def validate_enum_value(value, enum_class: enum.Enum) -> bool:
    """Validate if a value exists in an enum class."""
    try:
        enum_class(value)
    except ValueError:
        return False
    return True


def validate_recipe_data(data: ImmutableMultiDict) -> tuple[bool, tuple | None]:
    """
    Validate the incoming recipe data.

    Return whether the data is valid and if not an error response.
    """
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
    ingredients_ids: list[str], ingredients_quantities: list[str]
) -> dict[Ingredient, str | None] | None:
    """
    Validate ingredients and quantities.

    Raise ValueError if they are invalid.

    Return a dict that associates ingredient ids to their quantity.
    """
    # NOTE: if an ingredient is present multiple times the last occurrence will be the only one actually considered,
    # as in it will overwrite the precedent occurrences

    # If we got no ingredient ids we can early return None
    if not ingredients_ids:
        return None

    # Check that both lists have the same length
    if len(ingredients_ids) != len(ingredients_quantities):
        raise ValueError("Ingredients and quantities must have the same length")  # noqa: TRY003

    # Check that all ingredients are not Falsy values (empty strings)
    if not all(ingredients_ids):
        raise ValueError("Invalid ingredient IDs")  # noqa: TRY003

    # Convert empty strings to None
    quantities = [q if q.strip() else None for q in ingredients_quantities]

    # try to convert every id into an integer
    try:
        ids = list(map(int, ingredients_ids))
    except ValueError:
        raise ValueError("Invalid ingredient IDs") from None  # noqa: TRY003

    # get the actual ingredient objects from the db
    # implemented like this to not break if there are duplicates
    ingredients: list[Ingredient] = [db.session.get_one(Ingredient, i) for i in ids]

    # when wtforms validates the data submitted it automatically checks
    # that the value of a select is one of those sent to the client
    # so checking if the user can access the ingredient is not needed

    return dict(zip(ingredients, quantities, strict=True))
