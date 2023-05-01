"""
Filename: __init__.py

Purpose: This file defines a Flask blueprint for handling authentication-related routes and functions.

Dependencies:

Flask (version not specified)
Code structure:

Import the Flask Blueprint class from the flask module
Create a new blueprint instance with a name of 'auth_blueprint' and a URL prefix of ''
The blueprint instance is then used to define routes and functions related to authentication.
"""

from flask import Blueprint

blueprint = Blueprint(
    'auth_blueprint',
    __name__,
    url_prefix=''
)
