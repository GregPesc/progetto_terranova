import uuid
from io import BytesIO
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from PIL import Image

from app import csrf, db
from app.config import Config
from app.manage_recipes.forms import IngredientCreationForm, RecipeForm
from app.manage_recipes.utils import process_ingredients, validate_recipe_data
from app.models import (
    AlcoholicType,
    Category,
    Ingredient,
    LocalFavorite,
    UserDrink,
    drink_ingredient,
)

manage_recipes = Blueprint("manage_recipes", __name__)


@manage_recipes.route("/custom-recipe/add", methods=["GET", "POST"])
@login_required
def add_custom_recipe():
    """Handle the addition of a custom recipe using form data."""
    form = RecipeForm()

    # Populate dynamic form choices
    form.category.choices = [(c.value, c.value) for c in Category]
    form.alcoholic_type.choices = [(t.value, t.value) for t in AlcoholicType]

    ingredients = [
        ("", "Select an ingredient")  # Add default empty choice
    ] + [
        (i.id, i.name)
        for i in Ingredient.query.filter(
            (Ingredient.user == current_user) | (Ingredient.user == None)  # noqa: E711 # needs to use == instead of is, otherwise it breaks
        )
        .order_by(Ingredient.name)
        .all()
    ]
    for ingredient_form in form.ingredients:
        ingredient_form.ingredient.choices = ingredients

    if request.method == "POST":
        if form.validate_on_submit():
            is_valid, error_response = validate_recipe_data(request.form)
            if not is_valid:
                return error_response

            # validate the ingredients/quantities
            ids = [
                ingredient_form.ingredient.data for ingredient_form in form.ingredients
            ]
            quantities = [
                ingredient_form.quantity.data for ingredient_form in form.ingredients
            ]
            try:
                # remove last element since it is always empty from how the form is implemented
                ingredients_with_measure = process_ingredients(
                    ids[:-1], quantities[:-1]
                )
            except ValueError as e:
                return {"error": str(e)}, 400
            try:
                f_name = None
                # Handle file upload
                if form.thumbnail.data:
                    image_data = request.files[form.thumbnail.name].read()
                    img = Image.open(BytesIO(image_data))
                    f_name = str(uuid.uuid4()) + ".webp"
                    try:
                        img.save(Path(Config.UPLOAD_FOLDER) / Path(f_name))
                    except OSError as e:
                        return {
                            "error": "file format not valid",
                            "stack": str(e),
                        }, 400

                # Create and save the drink
                new_drink = UserDrink(
                    name=form.name.data,
                    category=Category(form.category.data),
                    alcoholic_type=AlcoholicType(form.alcoholic_type.data),
                    instructions=form.instructions.data,
                    thumbnail=f_name,
                    user=current_user,
                )
                db.session.add(new_drink)
                db.session.commit()

                # Add ingredients with their measures
                if ingredients_with_measure:
                    for ingredient, measure in ingredients_with_measure.items():
                        db.session.execute(
                            drink_ingredient.insert().values(
                                drink_id=new_drink.id,
                                ingredients_id=ingredient.id,
                                measure=measure,
                            )
                        )
                    db.session.commit()

                flash("Drink aggiunto con successo!", category="success")
                return redirect(url_for("main.mybar"))

            except ValueError as e:
                flash(str(e), category="error")
                return redirect(url_for("manage_recipes.add_custom_recipe"))
        else:
            flash("Dati errati.", category="error")

    return render_template("add_recipe.html", title="Aggiungi drink", form=form)


@manage_recipes.route("/custom-recipe/<string:drink_id>/delete", methods=["POST"])
@login_required
def delete_custom_recipe(drink_id):
    """
    Handle the deletion of a custom recipe.
    """

    try:
        drink_id = uuid.UUID(drink_id, version=4)
    except ValueError:
        return {"error": "Invalid drink_id"}, 400

    drink = UserDrink.query.get(drink_id)

    if not drink:
        return {"error": "Drink not found"}, 404

    if drink.user != current_user:
        return {"error": "Unauthorized"}, 403

    # Delete any associated favorite records
    LocalFavorite.query.filter_by(id=drink_id).delete()
    db.session.commit()

    # Delete the associated image file if it exists
    # sqlite non ha attivi di default i constraint chiave esterna quindi va fatto a mano
    if drink.thumbnail:
        image_path = Path(Config.UPLOAD_FOLDER) / Path(drink.thumbnail)
        if Path.exists(image_path):
            Path.unlink(image_path)

    db.session.delete(drink)
    db.session.commit()

    return "", 200


@manage_recipes.route("/manage-ingredients", methods=["GET", "POST"])
@login_required
def manage_ingredients():
    """Handle viewing, creating, and deleting custom ingredients."""
    form = IngredientCreationForm()

    if form.validate_on_submit():
        # Check if ingredient with same name already exists for this user
        existing = Ingredient.query.filter(
            (Ingredient.name == form.name.data)
            & ((Ingredient.user == current_user) | (Ingredient.user == None))  # noqa: E711
        ).first()

        if existing:
            flash(f"Ingrediente '{form.name.data}' già esistente.", category="error")
        else:
            # Create new ingredient
            new_ingredient = Ingredient(name=form.name.data, user=current_user)
            db.session.add(new_ingredient)
            db.session.commit()
            flash(
                f"Ingrediente '{form.name.data}' aggiunto con successo!",
                category="success",
            )
            return redirect(url_for("manage_recipes.manage_ingredients"))

    # Get all ingredients available to the user
    custom_ingredients = (
        Ingredient.query.filter(Ingredient.user == current_user)
        .order_by(Ingredient.name)
        .all()
    )
    standard_ingredients = (
        Ingredient.query.filter(Ingredient.user == None).order_by(Ingredient.name).all()  # noqa: E711
    )

    return render_template(
        "manage_ingredients.html",
        title="Gestisci Ingredienti",
        form=form,
        custom_ingredients=custom_ingredients,
        standard_ingredients=standard_ingredients,
    )


@manage_recipes.route("/delete-ingredient/<int:ingredient_id>", methods=["POST"])
@login_required
@csrf.exempt
def delete_ingredient(ingredient_id):
    """Handle the deletion of a custom ingredient."""
    ingredient = Ingredient.query.get(ingredient_id)

    if not ingredient:
        flash("Ingrediente non trovato", category="error")
        return redirect(url_for("manage_recipes.manage_ingredients"))

    # Ensure the user can only delete their own ingredients
    if ingredient.user != current_user:
        flash("Non sei autorizzato a eliminare questo ingrediente", category="error")
        return redirect(url_for("manage_recipes.manage_ingredients"))

    # Check if the ingredient is used in any recipes
    if ingredient.drinks:
        flash(
            f"Impossibile eliminare '{ingredient.name}': utilizzato in alcuni drink.",
            category="error",
        )
        return redirect(url_for("manage_recipes.manage_ingredients"))

    ingredient_name = ingredient.name
    db.session.delete(ingredient)
    db.session.commit()

    flash(
        f"Ingrediente '{ingredient_name}' eliminato con successo!", category="success"
    )
    return redirect(url_for("manage_recipes.manage_ingredients"))
