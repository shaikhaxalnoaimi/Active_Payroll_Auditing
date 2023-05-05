import pandas as pd

from application import db, create_app
from application.models import Role, User,UserRoles,keywords,system_high_ranking_positions


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
    # # Create a new user object
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
    data = pd.read_csv(r'C:\Users\nvtc\PycharmProjects\PayrollAuditing\application\populate_db\KEWORDS.csv')
    KEYWORD = data['KEYWORD'].values.tolist()
    LABEL = data['LABEL'].values.tolist()
    FILE_NAME = data['FILE_NAME'].values.tolist()
    # CREATED_DATE = data['CREATED_DATE'].values.tolist()
    # UPDATED_DATE = data['UPDATED_DATE'].values.tolist()
    CREATED_BY = data['CREATED_BY'].values.tolist()
    UPDATED_BY = data['UPDATED_BY'].values.tolist()

    for (k, l,fn,cb,ub) in zip(KEYWORD, LABEL,FILE_NAME,CREATED_BY,UPDATED_BY):
        new = keywords(k, l,fn,cb,ub)
        db.session.add(new)
        db.session.commit()

    # =================================================
    # positions
    # =================================================
    # Read the CSV file and insert the data into the database
    data = pd.read_csv(r'C:\Users\nvtc\PycharmProjects\PayrollAuditing\application\populate_db\HIGH_RANKING_POSITIONS.csv')
    POSITION_TITLE = data['POSITION_TITLE'].values.tolist()
    # CREATED_DATE = data['CREATED_DATE'].values.tolist()
    # UPDATED_DATE = data['UPDATED_DATE'].values.tolist()
    CREATED_BY = data['CREATED_BY'].values.tolist()
    UPDATED_BY = data['UPDATED_BY'].values.tolist()

    for (pt, cb,ub) in zip(POSITION_TITLE,CREATED_BY,UPDATED_BY):
        new = system_high_ranking_positions(pt,cb,ub)
        db.session.add(new)
        db.session.commit()

