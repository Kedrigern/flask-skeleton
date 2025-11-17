from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=40)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Password Confirmation",
        validators=[
            DataRequired(),
            EqualTo("password", message="Password does not match."),
        ],
    )
    submit = SubmitField("Register")
