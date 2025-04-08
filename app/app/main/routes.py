import uuid

import requests
from flask import (
    Blueprint,
    current_app,
    make_response,
    render_template,
    render_template_string,
    request,
    send_from_directory,
)
from flask_login import current_user, login_required
from sqlalchemy import or_, select

from app import db
from app.favorite.utils import is_api_favorite, is_local_favorite
from app.main.utils.history import (
    get_history_drinks,
    set_history_cookie,
    update_cocktail_history,
)
from app.models import (
    AlcoholicType,
    ApiDrink,
    ApiFavorite,
    Category,
    Ingredient,
    LocalFavorite,
    UserDrink,
    drink_ingredient,
)

main = Blueprint("main", __name__)

# API base URL used for catalog search
API_BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1/"


@main.route("/")
def home():
    drinks = get_history_drinks()
    return render_template("index.html", title="Applicazione", history=drinks)


@main.route("/catalogo")
def catalogo():
    drinks: list[ApiDrink] = ApiDrink.query.all()

    favorites = {}

    # If user is authenticated, check which drinks are favorites
    if current_user.is_authenticated:
        for drink in drinks:
            favorites[drink.id] = is_api_favorite(drink.id, current_user)

    # get all the ingredients from the db
    ingredients = db.session.execute(ingredients_query(current_user)).scalars().all()

    # Get categories and alcoholic types from enums
    categories = [(c.value, c.value) for c in Category]
    alcoholic_types = [(t.value, t.value) for t in AlcoholicType]

    return render_template(
        "catalogo.html",
        title="Catalogo",
        page_type="catalogo",
        drinks=drinks,
        favorites=favorites,
        ingredients=ingredients,
        categories=categories,
        alcoholic_types=alcoholic_types,
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
    ingredients = db.session.execute(ingredients_query(current_user)).scalars().all()

    # Get categories and alcoholic types from enums
    categories = [(c.value, c.value) for c in Category]
    alcoholic_types = [(t.value, t.value) for t in AlcoholicType]

    return render_template(
        "catalogo.html",
        title="My Bar",
        page_type="mybar",
        drinks=drinks,
        favorites=favorites,
        ingredients=ingredients,
        categories=categories,
        alcoholic_types=alcoholic_types,
    )


@main.route("/api/<int:drink_id>")
def specific_api(drink_id: int):
    # Query the external API for drink details by ID
    try:
        response = requests.get(
            API_BASE_URL + "lookup.php", timeout=5, params={"i": drink_id}
        ).json()

        # Check if the API returned valid data
        if not response.get("drinks"):
            return "Drink not found", 404

        # Extract the drink data from the response
        api_drink = response["drinks"][0]

        # Update history
        history_json = update_cocktail_history(drink_id)

        # Extract ingredients and their measures from the API response
        # The API returns ingredients as ingredientN and measures as measureN
        ingredients = []
        for i in range(1, 16):  # The API supports up to 15 ingredients
            ingredient = api_drink.get(f"strIngredient{i}")
            measure = api_drink.get(f"strMeasure{i}")

            # Only add if ingredient exists
            if ingredient and ingredient.strip():
                ingredients.append(
                    {
                        "name": ingredient.strip(),
                        "measure": measure.strip() if measure else None,
                    }
                )

        # Get the drink from database or create a new object for the template
        drink = ApiDrink.query.get(drink_id)
        if not drink:
            # If not in database, create a temporary object for the template
            drink = ApiDrink(
                id=drink_id,
                name=api_drink.get("strDrink"),
                thumbnail=api_drink.get("strDrinkThumb"),
            )

        drink.alcoholic_type = api_drink.get("strAlcoholic")
        drink.category = api_drink.get("strCategory")
        drink.instructions = api_drink.get("strInstructions")

        # Check if it's a favorite
        is_favorite = False
        if current_user.is_authenticated:
            is_favorite = is_api_favorite(drink_id, current_user)

        response = make_response(
            render_template(
                "cocktail.html",
                title=drink.name,
                drink=drink,
                ingredients=ingredients,
                is_favorite=is_favorite,
            )
        )

        # Set the updated history cookie
        response = set_history_cookie(response, history_json)

        return response  # noqa: RET504, TRY300

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later.", 504
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}", 500


@main.route("/local/<string:drink_id>")
@login_required
def specific_local(drink_id):
    try:
        drink_id = uuid.UUID(drink_id, version=4)
    except ValueError:
        return "Invalid drink id", 404

    drink = (
        db.session.query(UserDrink)
        .filter_by(id=drink_id, user_id=current_user.id)
        .first()
    )
    if not drink:
        return "Drink not found", 404

    # Update history using our utility function
    history_json = update_cocktail_history(drink.id, True)

    stmt = (
        select(Ingredient.name, drink_ingredient.c.measure)
        .join(drink_ingredient, Ingredient.id == drink_ingredient.c.ingredients_id)
        .where(drink_ingredient.c.drink_id == drink_id)
    )

    ingredient_data = db.session.execute(stmt).all()

    ingredients = [
        {"name": name, "measure": measure} for name, measure in ingredient_data
    ]

    # Check if it's a favorite
    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = is_local_favorite(drink.id, current_user)

    response = make_response(
        render_template(
            "cocktail.html",
            title=drink.name,
            drink=drink,
            ingredients=ingredients,
            is_favorite=is_favorite,
        )
    )

    # Use the utility function for setting the cookie
    response = set_history_cookie(response, history_json)

    return response  # noqa: RET504


@main.route("/htmx/filter-ingredients")
def filter_ingredients():
    search_term = request.args.get("search", "").lower()
    selected = set(request.args.getlist("selected"))  # Checked items from frontend
    # Get the page type to determine the filter URL
    page_type = request.args.get("page_type", "catalogo")

    # Fetch all ingredients from the database
    all_ingredients = [
        i.name
        for i in db.session.execute(ingredients_query(current_user)).scalars().all()
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
                hx-include="#filter-form, #main-search-bar"
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
    )


def ingredients_query(current_user):
    """Retrieve all ingredients available to the user."""
    try:
        user_id = current_user.id
    except AttributeError:
        user_id = None
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
    drink_name = request.args.get("name", "").strip()
    alcoholic_type = request.args.get("type", "")
    category = request.args.get("category", "")
    ingredient_names = request.args.getlist("ingredient[]")
    fav_only = request.args.get("fav_only", False)

    # Use the API to filter drinks
    result = {
        "name_query": None,
        "alcoholic_query": None,
        "category_query": None,
        "ingredient_query": None,
        "fav_drinks": None,
    }

    try:
        # Query by drink name - OR logic
        if drink_name:
            search_words = drink_name.split()
            combined_results = set()  # Will hold ALL drinks matching ANY search term

            # Try exact match first for full search term
            res = requests.get(
                API_BASE_URL + "search.php", timeout=5, params={"s": drink_name}
            ).json()
            exact_match_drinks = res.get("drinks")

            # Add exact matches to results
            if exact_match_drinks and isinstance(exact_match_drinks, list):
                exact_match_ids = {drink["idDrink"] for drink in exact_match_drinks}
                combined_results.update(exact_match_ids)

            # For multi-word searches, also search for each meaningful word individually (OR logic)
            if len(search_words) > 1:
                for word in search_words:
                    if (
                        len(word) > 2
                    ):  # Only search for words with more than 2 characters
                        word_res = requests.get(
                            API_BASE_URL + "search.php", timeout=5, params={"s": word}
                        ).json()
                        if word_res.get("drinks"):
                            # Add all drinks matching this word
                            word_match_ids = {
                                drink["idDrink"] for drink in word_res["drinks"]
                            }
                            combined_results.update(word_match_ids)

            result["name_query"] = combined_results if combined_results else set()

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

        if fav_only and current_user.is_authenticated:
            query = select(ApiDrink)
            query = query.join(ApiFavorite, ApiFavorite.id == ApiDrink.id)
            query = query.where(ApiFavorite.user_id == current_user.id)
            drinks: list[ApiDrink] = db.session.execute(query).scalars().all()
            if drinks:
                result["fav_drinks"] = {str(drink.id) for drink in drinks}
            else:
                result["fav_drinks"] = set()

        # Combine all queries
        filtered_ids = (
            set.intersection(*(query for query in result.values() if query is not None))
            if any(result.values())
            else set()
        )

        # If no filters applied, get all drinks
        if not any([drink_name, alcoholic_type, category, ingredient_names, fav_only]):
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
    drink_name = request.args.get("name", "").strip()
    alcoholic_type = request.args.get("type", "")
    category = request.args.get("category", "")
    ingredient_names = request.args.getlist("ingredient[]")
    fav_only = request.args.get("fav_only", False)

    query = select(UserDrink)

    if drink_name:
        search_words = drink_name.split()
        if len(search_words) > 1:
            # Multi-word search: each word should be present in the name
            for word in search_words:
                if len(word) > 2:  # Only filter on words with more than 2 characters
                    query = query.where(UserDrink.name.ilike(f"%{word}%"))
        else:
            # Single word search: use the original approach
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

    if fav_only:
        query = query.join(LocalFavorite, LocalFavorite.id == UserDrink.id)
        # query = query.where(LocalFavorite.user_id == current_user.id)

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
