import sqlite3
import pandas as pd
from flask_login import  current_user
from datetime import datetime
from application import db_path
from application.Control_Panel.validation import is_valid_input,sanitize_input



def createConnection():
    # connect to the database with a limited user
    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()

    # cur.execute("PRAGMA query_only = 1")

    return conn, cur

"""
This function to create HIGH_RANKING_POSITIONS Table (this is will not call at all just run it one time to create tables)
:return nothing
"""
def Create_Tables():
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    # Drop users table if already exsist.
    cur.execute("DROP TABLE IF EXISTS HIGH_RANKING_POSITIONS")


    # Create keywords table
    sql1 = '''CREATE TABLE "HIGH_RANKING_POSITIONS" (
                "PID"	INTEGER PRIMARY KEY AUTOINCREMENT,
                "POSITION_TITLE" TEXT,
                "CREATED_DATE" DATE ,
                "UPDATED_DATE" DATE ,
                "CREATED_BY" TEXT,
                "UPDATED_BY" TEXT)'''

    cur.execute(sql1)
    conn.commit()
    conn.close()



"""
This function to Fetch all high ranking positions title
:return all keywords df
"""
def Fetch_All_Positions():
    conn, cur = createConnection()
    # with sqlite3.connect(db_path) as cur:
    all_data = cur.execute('''select PID, POSITION_TITLE, CREATED_BY,CREATED_DATE, UPDATED_BY,UPDATED_DATE from HIGH_RANKING_POSITIONS ''')
    all_data = all_data.fetchall()
    all_data = pd.DataFrame(all_data, columns=['PID', 'POSITION_TITLE', 'CREATED_BY','CREATED_DATE' ,'UPDATED_BY','UPDATED_DATE'])

    return all_data

"""
This function to check if hte position high ranking already exist 
:param: receive the position title from forms
:return a df this dataframe will have data if the added position already exists and empty if added positio is successful and no duplicate
"""
def Check_No_Duplicate_Position(position_title):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    data = cur.execute('''select POSITION_TITLE from HIGH_RANKING_POSITIONS WHERE POSITION_TITLE=?''',(position_title,))
    data = data.fetchall()
    duplicate_position = pd.DataFrame(data,columns=['POSITION_TITLE'])
    return duplicate_position




def Insert_Data_Positions(position_titel):
    """
    This function to add new high ranking positions
    :param: receive the selected label and entered keyword from forms
    :return a df this dataframe will have data if the added keyword already exists and empty if added keyword is successful and no duplicate
    """
    # with sqlite3.connect(db_path) as cur:
    position_titel = position_titel.upper()
    created_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    created_by = current_user.username

    #fetch data if it is already exist in KEWORDS table
    duplicate_poistion = Check_No_Duplicate_Position(position_titel)

    if not duplicate_poistion.empty:
        validate = 'duplicate'
        return validate
    else:
        # validate = is_valid_input(position_titel)
        if not is_valid_input(position_titel):
            validate = 'invalid'
        else:
            position_titel = sanitize_input(position_titel)
            conn, cur = createConnection()
            cur.execute("insert into HIGH_RANKING_POSITIONS(POSITION_TITLE,CREATED_DATE,CREATED_BY) values (?,?,?)", (position_titel,created_date,created_by))
            conn.commit()
            conn.close()
            validate = 'True'
        return validate




"""
This function to edit high ranking positions 
:param: receive the id of position title
:return a df this dataframe will have data if the edited positions already exists and empty if added positions is successful and no duplicate
"""
def Edit_Positions(position_titel,uid):
    position_titel = position_titel.upper()
    updated_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = current_user.username
    # with sqlite3.connect(db_path) as cur:
        # fetch data if it is already exist in HIGH_RANKING_POSITIONS table
    duplicate_positions = Check_No_Duplicate_Position(position_titel)

        # if not duplicate_positions.empty:
        #     return duplicate_positions
        # else:
        #     cur.execute("update HIGH_RANKING_POSITIONS set POSITION_TITLE=?, UPDATED_BY=?,UPDATED_DATE=? where PID=?", (position_titel,updated_by,updated_date,uid))
        #     cur.commit()
        #     return duplicate_positions
        #



    if not duplicate_positions.empty:
        validate = 'duplicate'
        return validate
    else:
        # validate = is_valid_input(position_titel)
        if not is_valid_input(position_titel):
            validate = 'invalid'
        else:
            position_titel = sanitize_input(position_titel)
            conn, cur = createConnection()
            cur.execute(
                "update HIGH_RANKING_POSITIONS set POSITION_TITLE=?, UPDATED_BY=?,UPDATED_DATE=? where PID=?",
                (position_titel, updated_by, updated_date, uid))
            conn.commit()
            conn.close()
            validate = 'True'
        return validate




"""
This function to Fetch current position 
:param the position id 
:return position_title
"""
def Fetch_Current_Position_Values(uid):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    #Fetch Current Keyword
    current_position = cur.execute('''select POSITION_TITLE from HIGH_RANKING_POSITIONS WHERE PID=?''', (uid,))
    current_position = current_position.fetchall()
    current_position = pd.DataFrame(current_position, columns=['POSITION_TITLE'])
    current_position = current_position['POSITION_TITLE'][0]


    return current_position



"""
This function to delete the position title based on id
:param: receive the id of position title
:return nothing
"""
def Delete_Positions(uid):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    cur.execute("delete from HIGH_RANKING_POSITIONS where PID=?", (uid,))
    conn.commit()
    conn.close()


def fetchAllPositionTitle():
    """
    This function to Fetch all high ranking positions based on the selected label
    Returns
    -------
    all_data: list
        all high ranking positions title list
    """
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    all_data = cur.execute('''select POSITION_TITLE from HIGH_RANKING_POSITIONS''')

    all_data = all_data.fetchall()
    all_data = pd.DataFrame(all_data, columns=['POSITION_TITLE'])
    all_data = all_data['POSITION_TITLE'].values.tolist()

    return all_data

