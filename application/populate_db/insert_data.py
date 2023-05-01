import datetime

import pandas as pd

from application import db, create_app
from application.models import Role, User,UserRoles

app = create_app()

with app.app_context():
    user = Role('user')
    admin = Role('admin')
    roles = [user, admin]

    # =================================================
    # ROLE
    # =================================================
    for i in roles:
        db.session.add(i)
        db.session.commit()

    # =================================================
    # Users
    # =================================================
    # Create a new user object
    user = User(username='admin', password='admin')
    # Add the new user to the session
    db.session.add(user)
    # Commit the session to save the changes to the database
    db.session.commit()
    # Close the session
    db.session.close()


    # =================================================
    # User Roles
    # =================================================
    # Create a new user object
    user_role = UserRoles(user_id=1, role_id=1)
    # Add the new user to the session
    db.session.add(user_role)
    # Commit the session to save the changes to the database
    db.session.commit()
    # Close the session
    db.session.close()

    # =================================================
    # Keywords
    # =================================================
    # Read the CSV file and insert the data into the database
    data = pd.read_csv('users.csv')
    for row in data:
        user = User(username=row['username'], password=row['password'],
                    created_at=datetime.strptime(row['created_at'], '%Y-%m-%d %H:%M:%S'),
                    last_login=datetime.strptime(row['last_login'], '%Y-%m-%d %H:%M:%S'))
        db.session.add(user)
        db.session.commit()
        db.session.close()
