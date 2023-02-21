# import application
# from app import app
from application import db, create_app
from application.models import User

app = create_app()

with app.app_context():
    # =================================================
    # EMPLOYEE
    # =================================================
    emp = User("admin", "admin", "admin")
    db.session.add(emp)
    db.session.commit()

    # emp = User("admin3", "admin3", "admin3")
    # db.session.add(emp)
    # db.session.commit()