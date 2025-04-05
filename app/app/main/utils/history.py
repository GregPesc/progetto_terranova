import base64
import binascii
import contextlib
import json
import uuid

from flask import request
from flask_login import current_user

from app import db
from app.models import ApiDrink, UserDrink

MAX_HISTORY = 10


def load_history_cookie():
    """Load history from cookie and return as a Python list"""
    history_json = []
    try:
        if history_ids := request.cookies.get("history"):
            # Decode base64 string to JSON
            decoded = base64.b64decode(bytes(history_ids, "utf-8")).decode("utf-8")
            history_json = json.loads(decoded)
    except (json.JSONDecodeError, UnicodeDecodeError, binascii.Error):
        # If any decoding error occurs, just continue with empty history
        pass
    return history_json


def get_history_drinks():
    """Get drink objects from history cookie"""
    drinks = []
    history_json = load_history_cookie()

    for history_item in history_json:
        if history_item.get("source") == "local":
            with contextlib.suppress(Exception):
                drink_obj = db.session.execute(
                    db.select(UserDrink).filter_by(
                        user_id=current_user.id,
                        id=uuid.UUID(history_item.get("id"), version=4),
                    )
                ).scalar_one_or_none()

                if drink_obj:
                    drinks.append(drink_obj)
        elif history_item.get("source") == "api":
            with contextlib.suppress(Exception):
                drink_obj = db.session.query(ApiDrink).get(history_item.get("id"))
                if drink_obj:
                    drinks.append(drink_obj)
    return drinks


def set_history_cookie(response, history_json):
    """Set the encoded history cookie on the given response object"""
    encoded = base64.b64encode(bytes(json.dumps(history_json), "utf-8")).decode("utf-8")
    response.set_cookie(
        "history",
        value=encoded,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite="Lax",
    )
    return response


def update_cocktail_history(cocktail_id, is_local=False):
    """Update history list with a new cocktail visit"""
    history_json = load_history_cookie()
    history_json.insert(
        0, {"id": str(cocktail_id), "source": "local" if is_local else "api"}
    )
    return history_json[:MAX_HISTORY]
