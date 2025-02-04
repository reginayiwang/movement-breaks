from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectMultipleField
from wtforms.validators import InputRequired

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class SettingsForm(FlaskForm):
    work_length = IntegerField("Work Length (minutes)")
    break_length = IntegerField("Break Length (minutes)")
    equipment = SelectMultipleField("Equipment", coerce=int)
    targets = SelectMultipleField("Exercise Targets", coerce=int)
