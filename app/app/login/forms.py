from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Ricordami")
    submit = SubmitField("Accedi")


class RegisterForm(FlaskForm):
    def validate_email(form, field):
        user = db.session.execute(
            db.select(User).filter_by(email=field.data.lower())
        ).first()

        if user:
            return ValidationError("Email già esitente. Esegui il login.")

        return None

    email = EmailField("Email", validators=[InputRequired(), Email(), validate_email])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Conferma password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Registrati")
