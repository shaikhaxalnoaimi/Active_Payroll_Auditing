from flask import Flask
from flask_moment import Moment
from importlib import import_module
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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


def register_extensions(app):
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
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
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/nao_db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    SECRET_KEY = 'S#perS3crEt_007'
    app.config['SECRET_KEY'] = SECRET_KEY
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
