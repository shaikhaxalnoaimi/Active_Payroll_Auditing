"""
Filename: application\home\__init__.py

Purpose: This file defines a Flask blueprint for the home page of a web application.

Dependencies:
-	Flask (2.2.3)

Code structure:

Import the Blueprint class from the Flask module
Create a new blueprint object named 'home_blueprint'
Pass the following arguments to the Blueprint constructor:
'home_blueprint' as the name of the blueprint
'name' as the name of the current Python module
An empty string as the URL prefix for all routes in this blueprint
The resulting blueprint object is stored in the 'blueprint' variable.
"""


from flask import Blueprint

blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix=''

)
