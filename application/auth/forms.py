"""
Filename: forms.py

Purpose: This file contains the FlaskForm classes for the login form.

Dependencies with version:

Flask-WTF (0.14.3)
WTForms (2.3.3)
Code structure:

Import necessary modules and classes
Define LoginForm class that inherits from FlaskForm
Define fields for the login form (username and password)
Add validators to the fields
Add RecaptchaField if necessary (not included in this example)
Return the form class for use in the application.
"""

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


# login


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_login',
                           validators=[DataRequired()]
                           )
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()]
                             )


