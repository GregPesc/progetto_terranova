import requests
from flask import Blueprint, abort, request
from flask_login import current_user, login_required
from sqlalchemy import select

from app import db
from app.models import Ingredient, UserDrink, drink_ingredient

search = Blueprint("search", __name__)

API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"


@search.route("/api/search/catalog")
def catalog_search():
    drink_name = request.args.get("name", None)
    alcoholic_type = request.args.get("type", None)
    category = request.args.get("category", None)
    ingredient_names = request.args.getlist("ingredient")

    result = {
        "name_query": None,
        "alcoholic_query": None,
        "category_query": None,
        "ingredient_query": None,
    }
    try:
        # Query by drink name
        if drink_name:
            res = requests.get(
                API_BASE_URL + "/search.php", timeout=5, params={"s": drink_name}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):  # Ensure drinks is a list
                result["name_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["name_query"] = set()

        # Query by alcoholic type
        if alcoholic_type:
            res = requests.get(
                API_BASE_URL + "/filter.php", timeout=5, params={"a": alcoholic_type}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):  # Ensure drinks is a list
                result["alcoholic_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["alcoholic_query"] = set()

        # Query by category
        if category:
            res = requests.get(
                API_BASE_URL + "/filter.php", timeout=5, params={"c": category}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):  # Ensure drinks is a list
                result["category_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["category_query"] = set()

        # Query by ingredients (multiple)
        if ingredient_names:
            ingredient_sets: list[set] = []
            for ingredient_name in ingredient_names:
                res = requests.get(
                    API_BASE_URL + "/filter.php",
                    timeout=5,
                    params={"i": ingredient_name},
                ).json()
                drinks = res.get("drinks")
                # when drinks are found drinks is a list of ids, otherwise it is a string ('no data found')
                if drinks and isinstance(drinks, list):
                    ingredient_sets.append({drink["idDrink"] for drink in drinks})
                else:
                    ingredient_sets.append(set())

            # Combine ingredient sets (intersection of all)
            result["ingredient_query"] = (
                set.intersection(*ingredient_sets) if ingredient_sets else set()
            )
    except requests.exceptions.Timeout:
        abort(500)

    # Combine all queries
    combined_results = (
        set.intersection(*(query for query in result.values() if query is not None))
        if any(result.values())
        else set()
    )

    # Create the response
    return {"drinks_ids": list(combined_results)}


@search.route("/api/search/mybar")
@login_required
def bar_search():
    drink_name = request.args.get("name", None)
    alcoholic_type = request.args.get("type", None)
    category = request.args.get("category", None)
    ingredient_names = request.args.getlist("ingredient")  # Allow multiple ingredients

    # if no parameters are sent all drinks are sent back

    query = select(UserDrink)

    if drink_name:
        query = query.where(UserDrink.name.ilike(f"%{drink_name}%"))

    if alcoholic_type:
        query = query.where(UserDrink.alcoholic_type == alcoholic_type)

    if category:
        query = query.where(UserDrink.category == category)

    if ingredient_names:
        for ingredient_name in ingredient_names:
            query = query.where(
                UserDrink.ingredients.any(Ingredient.name.ilike(f"%{ingredient_name}%"))
            )

    query = query.where(UserDrink.user == current_user)

    drinks = db.session.execute(query).scalars().all()

    result = []
    for drink in drinks:
        ingredients_query = (
            select(Ingredient.name, drink_ingredient.c.measure)
            .join(drink_ingredient, Ingredient.id == drink_ingredient.c.ingredients_id)
            .where(drink_ingredient.c.drink_id == drink.id)
        )

        ingredients = db.session.execute(ingredients_query).all()

        result.append(
            {
                "id": drink.id,
                "name": drink.name,
                "category": drink.category.value,
                "alcoholic_type": drink.alcoholic_type.value,
                "instructions": drink.instructions,
                "thumbnail": drink.thumbnail,
                "ingredients": [
                    {"name": ingredient[0], "measure": ingredient[1]}
                    for ingredient in ingredients
                ],
            }
        )

    return {"drinks": result}
