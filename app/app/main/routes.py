import requests
from flask import (
    Blueprint,
    current_app,
    render_template,
    render_template_string,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from app import db
from app.favorite.utils import is_api_favorite, is_local_favorite
from app.models import AlcoholicType, ApiDrink, Category, Ingredient, UserDrink

main = Blueprint("main", __name__)

# API base URL used for catalog search
API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"


@main.route("/")
def home():
    return render_template("index.html", title="Applicazione")


@main.route("/catalogo")
def catalogo():
    drinks: list[ApiDrink] = ApiDrink.query.all()

    favorites = {}

    # If user is authenticated, check which drinks are favorites
    if current_user.is_authenticated:
        for drink in drinks:
            favorites[drink.id] = is_api_favorite(drink.id, current_user)

    # get all the ingredients from the db
    ingredients = db.session.execute(ingredients_query(current_user.id)).scalars().all()

    return render_template(
        "catalogo.html",
        title="Catalogo",
        page_type="catalogo",
        drinks=drinks,
        favorites=favorites,
        ingredients=ingredients,
    )


@main.route("/mybar")
@login_required
def mybar():
    drinks: list[UserDrink] = UserDrink.query.all()

    favorites = {}

    # If user is authenticated, check which drinks are favorites
    if current_user.is_authenticated:
        for drink in drinks:
            favorites[drink.id] = is_local_favorite(drink.id, current_user)

    # get all the ingredients from the db
    ingredients = db.session.execute(ingredients_query(current_user.id)).scalars().all()

    return render_template(
        "catalogo.html",
        title="My Bar",
        page_type="mybar",
        drinks=drinks,
        favorites=favorites,
        ingredients=ingredients,
    )


@main.route("/htmx/filter-ingredients")
def filter_ingredients():
    search_term = request.args.get("search", "").lower()
    selected = set(request.args.getlist("selected"))  # Checked items from frontend
    # Get the page type to determine the filter URL
    page_type = request.args.get("page_type", "catalogo")

    # Fetch all ingredients from the database
    all_ingredients = [
        i.name
        for i in db.session.execute(ingredients_query(current_user.id)).scalars().all()
    ]

    # Filter ingredients based on the search term
    filtered = [i for i in all_ingredients if search_term in i.lower()]

    # Merge checked + filtered items to ensure persistence
    combined = list(selected | set(filtered))

    # Sort the ingredients alphabetically
    combined.sort()

    # Render the updated checkboxes, keeping selected items checked and including HTMX attributes
    return render_template_string(
        """
        {% for i in ingredients %}
        <div class="cell">
          <label class="checkbox">
            <input type="checkbox" name="ingredient[]" value="{{ i }}"
                {% if i in selected %}checked{% endif %}
                hx-trigger="change"
                hx-include="#filter-form"
                hx-get="{% if page_type == 'mybar' %}{{ url_for('main.filter_mybar') }}{% else %}{{ url_for('main.filter_catalog') }}{% endif %}"
                hx-target="#drinks-container">
            {{ i }}
          </label>
        </div>
        {% endfor %}
        """,
        ingredients=combined,
        selected=selected,
        page_type=page_type,
        url_for=url_for,  # Pass url_for to the template
    )


def ingredients_query(user_id):
    """Retrieve all ingredients available to the user."""
    return (
        db.select(Ingredient)
        .order_by(Ingredient.name)
        .where(
            or_(Ingredient.user_id == user_id, Ingredient.user == None)  # noqa: E711
        )
    )


@main.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


@main.route("/htmx/filter-catalog")
def filter_catalog():
    """Filter catalog drinks with HTMX."""
    drink_name = request.args.get("name", "")
    alcoholic_type = request.args.get("type", "")
    category = request.args.get("category", "")
    ingredient_names = request.args.getlist("ingredient[]")

    # Use the API to filter drinks
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
                API_BASE_URL + "search.php", timeout=5, params={"s": drink_name}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):
                result["name_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["name_query"] = set()

        # Query by alcoholic type
        if alcoholic_type:
            res = requests.get(
                API_BASE_URL + "filter.php", timeout=5, params={"a": alcoholic_type}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):
                result["alcoholic_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["alcoholic_query"] = set()

        # Query by category
        if category:
            res = requests.get(
                API_BASE_URL + "filter.php", timeout=5, params={"c": category}
            ).json()
            drinks = res.get("drinks")
            if drinks and isinstance(drinks, list):
                result["category_query"] = {drink["idDrink"] for drink in drinks}
            else:
                result["category_query"] = set()

        # Query by ingredients (multiple)
        if ingredient_names:
            ingredient_sets = []
            for ingredient_name in ingredient_names:
                res = requests.get(
                    API_BASE_URL + "filter.php",
                    timeout=5,
                    params={"i": ingredient_name},
                ).json()
                drinks = res.get("drinks")
                if drinks and isinstance(drinks, list):
                    ingredient_sets.append({drink["idDrink"] for drink in drinks})
                else:
                    ingredient_sets.append(set())

            # Combine ingredient sets (intersection of all)
            result["ingredient_query"] = (
                set.intersection(*ingredient_sets) if ingredient_sets else set()
            )

        # Combine all queries
        filtered_ids = (
            set.intersection(*(query for query in result.values() if query is not None))
            if any(result.values())
            else set()
        )

        # If no filters applied, get all drinks
        if not any([drink_name, alcoholic_type, category, ingredient_names]):
            drinks = ApiDrink.query.all()
        else:
            # Get drinks by ID
            drinks = ApiDrink.query.filter(ApiDrink.id.in_(filtered_ids)).all()

        favorites = {}
        if current_user.is_authenticated:
            for drink in drinks:
                favorites[drink.id] = is_api_favorite(drink.id, current_user)

        return render_template(
            "partials/drink_cards.html",
            drinks=drinks,
            favorites=favorites,
            page_type="catalogo",
        )

    except requests.exceptions.Timeout:
        return "<div class='notification is-danger'>La richiesta ha impiegato troppo tempo. Riprova più tardi.</div>"


@main.route("/htmx/filter-mybar")
@login_required
def filter_mybar():
    """Filter mybar drinks with HTMX."""
    drink_name = request.args.get("name", "")
    alcoholic_type = request.args.get("type", "")
    category = request.args.get("category", "")
    ingredient_names = request.args.getlist("ingredient[]")

    query = select(UserDrink)

    # Apply filters
    if drink_name:
        query = query.where(UserDrink.name.ilike(f"%{drink_name}%"))

    if alcoholic_type:
        query = query.where(UserDrink.alcoholic_type == AlcoholicType(alcoholic_type))

    if category:
        query = query.where(UserDrink.category == Category(category))

    if ingredient_names:
        for ingredient_name in ingredient_names:
            query = query.where(
                UserDrink.ingredients.any(Ingredient.name.ilike(f"%{ingredient_name}%"))
            )

    # Only show user's drinks
    query = query.where(UserDrink.user == current_user)

    drinks = db.session.execute(query).scalars().all()

    favorites = {}
    for drink in drinks:
        favorites[drink.id] = is_local_favorite(drink.id, current_user)

    return render_template(
        "partials/drink_cards.html",
        drinks=drinks,
        favorites=favorites,
        page_type="mybar",
    )
