import jinja2
from flask import Flask

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.jinja_env.autoescape = jinja2.select_autoescape()
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    from app.main.routes import main

    app.register_blueprint(main)

    return app
