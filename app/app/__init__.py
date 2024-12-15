import flask_login
import flask_sqlalchemy
import jinja2
import sqlalchemy
from flask import Flask

from app.config import Config


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


db = flask_sqlalchemy.SQLAlchemy(model_class=Base)

login_manager = flask_login.LoginManager()

from .models import *  # noqa: E402, F403


def create_app(config_class=Config):
    # Flask configuration
    app = Flask(__name__)
    app.config.from_object(Config)

    # Jinja configuration
    app.jinja_env.autoescape = jinja2.select_autoescape()
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    db.init_app(app)
    login_manager.init_app(app)

    from app.main.routes import main

    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
