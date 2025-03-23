from flask import (
    Blueprint,
    current_app,
    render_template,
    render_template_string,
    request,
    send_from_directory,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

from app import db
from app.favorite.utils import is_api_favorite, is_local_favorite
from app.models import ApiDrink, Ingredient, UserDrink

main = Blueprint("main", __name__)


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

    # Render the updated checkboxes, keeping selected items checked
    return render_template_string(
        """
        {% for i in ingredients %}
        <div class="cell">
          <label class="checkbox">
            <input type="checkbox" name="ingredient[]" value="{{ i }}"
                {% if i in selected %}checked{% endif %}>
            {{ i }}
          </label>
        </div>
        {% endfor %}
    """,
        ingredients=combined,
        selected=selected,
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
