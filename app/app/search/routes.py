import requests
from flask import Blueprint, abort, request

search = Blueprint("search", __name__)

API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"


@search.route("/api/catalog-search")
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
            ingredient_sets = []
            for ingredient_name in ingredient_names:
                res = requests.get(
                    API_BASE_URL + "/filter.php",
                    timeout=5,
                    params={"i": ingredient_name},
                ).json()
                drinks = res.get("drinks")
                if drinks and isinstance(drinks, list):  # Ensure drinks is a list
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


def bar_search(): ...
