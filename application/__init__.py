"""
Filename: app.py

Purpose: This file is the main entry point for the Flask application. It creates the Flask app, registers extensions, blueprints, and creates the database tables.

Dependencies:

Flask (version not specified)
Flask-Moment (version not specified)
Flask-SQLAlchemy (version not specified)
Flask-Login (version not specified)
Flask-Limiter (version not specified)
os (built-in module)
import_module (built-in module)
Code structure:

The file starts with importing necessary modules and defining some helper functions.
Then, the app is created with necessary configurations.
The register_extensions() function is called to register Flask extensions.
The register_blueprints() function is called to register Flask blueprints.
The database tables are created with db.create_all() function.
Finally, the app is returned.
"""

from flask import Flask
from flask_moment import Moment
from importlib import import_module
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


def base_dir():
    """

    Returns
    -------
    base directory of the current file to use it in any path to be dynamic
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    return BASE_DIR

def generate_report_path():
    BASE_DIR = base_dir()
    gen_report_path = os.path.join(BASE_DIR, "data", "Generated Report")
    return gen_report_path


def generate_allowancefile_path():
    BASE_DIR = base_dir()
    gen_allow_path = os.path.join(BASE_DIR, "data", "AllowanceFiles")
    return gen_allow_path

def generate_high_position_file_path():
    BASE_DIR = base_dir()
    gen_highrank_path = os.path.join(BASE_DIR, "data", "HighPosition Rules")
    return gen_highrank_path

def organized_allowance_file():
    BASE_DIR = base_dir()
    gen_allow_path = os.path.join(BASE_DIR, "data", "Organized Allowance Files")
    return gen_allow_path



def organized_overtime_file():
    BASE_DIR = base_dir()
    gen_overtime_path = os.path.join(BASE_DIR, "data", "Overtime Rules")
    return gen_overtime_path

moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data", "nao_db.sqlite3")
limiter = Limiter(get_remote_address,default_limits=["200 per day", "50 per hour"])



def register_extensions(app):
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    limiter.init_app(app)
    # sess = Session()
    # sess.init_app(app)

def register_blueprints(app):
    home_module = import_module('application.home.routes')
    app.register_blueprint(home_module.blueprint)

    auth_module = import_module('application.auth.routes')
    app.register_blueprint(auth_module.blueprint)


    controlpanel_module = import_module('application.Control_Panel.routes')
    app.register_blueprint(controlpanel_module.blueprint, name="control_panel")





def create_app():
    # app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/nao_db.sqlite3'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nao_db.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.secret_key = 'jose'
    # api = Api(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    app.config["UPLOAD_FOLDER"] = r'uploads/'
    app.config["ALLOWED_EXTENSIONS"] = ['.xlsx']
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1000 * 1000
    # app.config["SESSION_TYPE"] = "filesystem"
    register_extensions(app)
    register_blueprints(app)



    with app.app_context():
        db.create_all()  # Create database tables for our data models

        return app
