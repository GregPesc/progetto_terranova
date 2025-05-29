import json

from flask import Blueprint, current_app, flash, jsonify, render_template, request
from flask_login import login_required
from google import genai

from app.ai.forms import CocktailInventionForm

ai = Blueprint("ai", __name__)


def get_gemini_model():
    """Get configured Gemini model with API key from Flask config."""
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in configuration")  # noqa: TRY003

    return genai.Client(api_key=api_key)


class CocktailParseError(Exception):
    """Custom exception for cocktail parsing errors."""


def create_cocktail_prompt(ingredients: str, description: str) -> str:
    """Create a structured prompt for Gemini to generate cocktail recipes."""
    return f"""
You are a professional mixologist tasked with creating an original cocktail recipe.
Based on the user's preferences, create a unique cocktail that doesn't exist in any known cocktail database.

User's favorite ingredients: {ingredients}
User's description: {description}

Create a completely original cocktail recipe and respond ONLY with a valid JSON object in this exact format:
{{
    "name": "Creative cocktail name",
    "ingredients": [
        {{"name": "ingredient name", "measure": "amount (e.g., 2 oz, 1 dash, etc.)"}},
        {{"name": "ingredient name", "measure": "amount"}}
    ],
    "instructions": "Step-by-step preparation instructions",
    "description": "Brief description of the cocktail's taste and character",
    "garnish": "Garnish recommendation (optional)"
}}

Requirements:
- Use at least 2 of the user's favorite ingredients
- Create a completely original name (not an existing cocktail)
- Include 3-6 ingredients total
- Provide clear measurements in metric units (e.g., ml, cl) or standard measures (e.g., oz, dash)
- Give detailed preparation instructions
- Make it sound delicious and unique

Respond ONLY with the JSON object, no additional text. The name, ingredients, instructions, and description must be in the language the user uses, if in doubt use English.
"""


def _validate_cocktail_data(cocktail_data: dict) -> None:
    """Validate the cocktail data structure."""
    required_fields = ["name", "ingredients", "instructions"]
    for field in required_fields:
        if field not in cocktail_data:
            raise CocktailParseError(f"Missing required field: {field}")  # noqa: TRY003

    if (
        not isinstance(cocktail_data["ingredients"], list)
        or len(cocktail_data["ingredients"]) == 0
    ):
        raise CocktailParseError("Ingredients must be a non-empty list")  # noqa: TRY003

    for ingredient in cocktail_data["ingredients"]:
        if (
            not isinstance(ingredient, dict)
            or "name" not in ingredient
            or "measure" not in ingredient
        ):
            raise CocktailParseError(  # noqa: TRY003
                "Each ingredient must have 'name' and 'measure' fields"
            )


def parse_gemini_response(response_text: str) -> dict[str, object]:
    """Parse and validate the Gemini response."""
    try:
        # Try to extract JSON from the response
        response_text = response_text.strip()

        # Sometimes the API returns text before/after the JSON, so try to extract it
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            raise CocktailParseError("No JSON found in response")  # noqa: TRY003, TRY301

        json_str = response_text[start_idx:end_idx]
        cocktail_data = json.loads(json_str)

        # Validate required fields
        _validate_cocktail_data(cocktail_data)

        return cocktail_data  # noqa: TRY300

    except json.JSONDecodeError as e:
        raise CocktailParseError(f"Invalid JSON format: {e!s}") from e  # noqa: TRY003
    except CocktailParseError:
        raise
    except Exception as e:
        raise CocktailParseError(f"Error parsing response: {e!s}") from e  # noqa: TRY003


@ai.route("/invent-cocktail", methods=["GET", "POST"])
@login_required
def invent_cocktail():
    """Handle cocktail invention requests using Gemini AI."""
    form = CocktailInventionForm()
    cocktail_data = None
    error_message = None

    if form.validate_on_submit():
        try:
            # Create the prompt
            prompt = create_cocktail_prompt(
                form.ingredients.data, form.description.data
            )

            # Initialize the Gemini model
            client = get_gemini_model()

            # Generate the cocktail recipe
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt
            )

            if not response.text:
                raise CocktailParseError("Empty response from Gemini API")  # noqa: TRY003, TRY301

            # Parse and validate the response
            cocktail_data = parse_gemini_response(response.text)

            flash("Cocktail inventato con successo!", "success")

        except (CocktailParseError, ValueError) as e:
            error_message = f"Errore nella generazione del cocktail: {e!s}"
            flash(error_message, "error")

    return render_template(
        "ai/invent_cocktail.html",
        form=form,
        cocktail_data=cocktail_data,
        error_message=error_message,
        title="Inventa il tuo Cocktail",
    )


@ai.route("/api/invent-cocktail", methods=["POST"])
@login_required
def api_invent_cocktail():
    """API endpoint for cocktail invention (for AJAX requests)."""
    try:
        data = request.get_json()  # Check if API key is configured
        if not data or "ingredients" not in data or "description" not in data:
            return jsonify(
                {"error": "Missing required fields: ingredients, description"}
            ), 400

        # Create the prompt
        prompt = create_cocktail_prompt(data["ingredients"], data["description"])

        # Initialize the Gemini model
        client = get_gemini_model()

        # Generate the cocktail recipe
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )

        if not response.text:
            return jsonify(
                {"error": "Empty response from Gemini API"}
            ), 500  # Parse and validate the response
        cocktail_data = parse_gemini_response(response.text)

        return jsonify({"success": True, "cocktail": cocktail_data})

    except (CocktailParseError, ValueError) as e:
        return jsonify({"error": f"Error generating cocktail: {e!s}"}), 500
