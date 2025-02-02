import uuid

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import csrf, db
from app.manage_recipes.utils import process_ingredients, validate_recipe_data
from app.models import AlcoholicType, Category, UserDrink, drink_ingredient

manage_recipes = Blueprint("manage_recipes", __name__)


@manage_recipes.route("/custom-recipe/add", methods=["GET", "POST"])
@login_required
def add_custom_recipe():
    """
    Handle the addition of a custom recipe.

    Input: POST request with mimetype application/json

    {
        "name": str,  # Name of the drink
        "category": str,  # Category of the drink (e.g., Cocktail, Shot)
        "alcoholic_type": str,  # Type of the drink (e.g., Alcoholic, Non alcoholic)
        "instructions": str,  # (Optional) Instructions for making the drink
        "thumbnail": str,  # (Optional) URL to the thumbnail image of the drink
        "ingredients_ids": str,  # Comma-separated string of ingredient IDs
        "ingredients_quantities": str  # Comma-separated string of ingredient quantities
    }
    """

    if request.method == "POST":
        data: dict = request.json

        # Validate input data
        is_valid, error_response = validate_recipe_data(data)
        if not is_valid:
            return error_response

        try:
            # Process ingredients
            ingredients, ingredient_quantities = process_ingredients(
                data.get("ingredients_ids"), data.get("ingredients_quantities")
            )

            # Create and save the drink
            new_drink = UserDrink(
                name=data["name"],
                category=Category(data["category"]),
                alcoholic_type=AlcoholicType(data["alcoholic_type"]),
                instructions=data.get("instructions"),
                thumbnail=data.get("thumbnail"),
                user_id=current_user.id,
            )
            db.session.add(new_drink)
            db.session.commit()

            # Add ingredients with their measures
            if ingredients and ingredient_quantities:
                for ingredient in ingredients:
                    db.session.execute(
                        drink_ingredient.insert().values(
                            drink_id=new_drink.id,
                            ingredients_id=ingredient.id,
                            measure=ingredient_quantities.get(ingredient.id),
                        )
                    )
                db.session.commit()

        except ValueError as e:
            return {"error": str(e)}, 400

        # this runs only if no exceptions were raised in the try block
        else:
            flash("Drink aggiunto con successo!", category="success")
            return redirect(url_for("main.home"))

    else:
        return render_template("add_recipe.html")


@manage_recipes.route("/custom-recipe/delete", methods=["POST"])
@login_required
@csrf.exempt  # TODO: controlla se si può rimuovere
def delete_custom_recipe():
    """
    Handle the deletion of a custom recipe.

    Input: POST request with mimetype application/json

    {
        "drink_id": UUID  # ID of the drink to delete
    }
    """

    data: dict = request.json
    drink_id = data.get("drink_id")

    try:
        drink_id = uuid.UUID(drink_id, version=4)
    except ValueError:
        return {"error": "Invalid drink_id"}, 400

    if not drink_id:
        return {"error": "Missing drink_id"}, 400

    drink = UserDrink.query.get(drink_id)

    if not drink:
        return {"error": "Drink not found"}, 404

    if drink.user != current_user:
        return {"error": "Unauthorized"}, 403

    db.session.delete(drink)
    db.session.commit()

    return {"message": "Drink deleted successfully"}, 200
