from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectMultipleField
from wtforms.validators import InputRequired

class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class SettingsForm(FlaskForm):
    """Form for user settings"""
    work_length = IntegerField("Work Length (minutes)")
    break_length = IntegerField("Break Length (minutes)")
    equipment = SelectMultipleField("Equipment", coerce=int)
    targets = SelectMultipleField("Exercise Targets", coerce=int)
