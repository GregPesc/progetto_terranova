import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    UPLOAD_FOLDER = BASE_DIR / "uploads"
