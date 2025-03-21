from pathlib import Path

import flask_login
import flask_sqlalchemy
import jinja2
import sqlalchemy
from flask import Flask
from flask_wtf import CSRFProtect

from app.config import Config


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


db = flask_sqlalchemy.SQLAlchemy(model_class=Base)
login_manager = flask_login.LoginManager()
login_manager.login_view = "login.login_route"
login_manager.login_message_category = "info"
csrf = CSRFProtect()

from .models import *  # noqa: E402, F403


def create_app(config_class=Config):
    # Flask configuration
    app = Flask(__name__)
    app.config.from_object(Config)

    # Jinja configuration
    app.jinja_env.autoescape = jinja2.select_autoescape()
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Create the necessary directories
    Path.mkdir(Path(Config.UPLOAD_FOLDER), parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.favorite.routes import favorite
    from app.login.routes import login
    from app.main.routes import main
    from app.manage_recipes.routes import manage_recipes
    from app.random.routes import random
    from app.search.routes import search

    app.register_blueprint(favorite)
    app.register_blueprint(login)
    app.register_blueprint(main)
    app.register_blueprint(manage_recipes)
    app.register_blueprint(random)
    app.register_blueprint(search)

    with app.app_context():
        db.create_all()

    return app
