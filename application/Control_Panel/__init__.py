"""
Filename: application\Control_Panel\__init__.py

Purpose: This file defines a Flask blueprint for the home page of a web application.

Dependencies:

Flask (version not specified)
Code structure:

Import the Blueprint class from the Flask module
Create a new blueprint object named 'home_blueprint'
Set the blueprint's name to 'home_blueprint'
Set the blueprint's import name to 'name'
Set the blueprint's URL prefix to an empty string (indicating that this blueprint will handle requests to the root URL)
No routes or views are defined in this file, as those will be added in other files that import this blueprint.

"""


from flask import Blueprint
blueprint = Blueprint(
    'home_blueprint',
    __name__,
    url_prefix=''

)





# create connection to the db
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # print(BASE_DIR)
# # string2 = BASE_DIR.replace('\\n', ' ')
# # print(string2)
#
# # db_path1 = os.path.join("/NAO-Payroll/application/", "nao_db.sqlite3")
# db_path = os.path.join(BASE_DIR, "nao_db.sqlite3")
# # r'a\\nb'.replace('\\\\', '\\')
# print(db_path)
# # print(db_path1)
