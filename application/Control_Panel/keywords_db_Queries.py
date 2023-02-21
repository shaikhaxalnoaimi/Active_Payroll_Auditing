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
This function to create Tables (this is will not call at all just run it one time to create tables)
:return nothing
"""
def Create_Tables():
    # with sqlite3.connect(db_path) as cur:
        # Drop users table if already exsist.
        #cur.execute("DROP TABLE IF EXISTS KEWORDS")
    conn, cur = createConnection()
    #Create keywords table
    sql ='''CREATE TABLE "KEWORDS" (
            "KID"	INTEGER PRIMARY KEY AUTOINCREMENT,
            "KEYWORD" TEXT,
            "LABEL"	TEXT,
            "FILE_NAME" TEXT,
            "CREATED_DATE" DATE ,
            "UPDATED_DATE" DATE ,
            "CREATED_BY" TEXT,
            "UPDATED_BY" TEXT)'''

    cur.execute(sql)
    conn.commit()
    conn.close()

"""
This function to Fetch all keywords based on the selected label 
:return all keywords df
"""
def Fetch_All_Keywords(file_name,selected_value):
    # with sqlite3.connect(db_path) as cur:
        #selected_value ='CPR_NO'

        # Create a Connection
        # print(selected_value)
    conn, cur = createConnection()
    if file_name == "MASTER":
        all_data = cur.execute('''select KID, FILE_NAME, LABEL,KEYWORD, CREATED_BY,CREATED_DATE, UPDATED_BY,UPDATED_DATE from KEWORDS WHERE LABEL=? AND FILE_NAME=?''',(selected_value,file_name))
    elif file_name == "PAYROLL":
        all_data = cur.execute('''select KID, FILE_NAME, LABEL, KEYWORD,CREATED_BY,CREATED_DATE, UPDATED_BY,UPDATED_DATE from KEWORDS WHERE LABEL=? AND FILE_NAME=?''',(selected_value,file_name))

    all_data = all_data.fetchall()
    all_data = pd.DataFrame(all_data, columns=['KID', 'FILE_NAME', 'LABEL', 'KEYWORD','CREATED_BY','CREATED_DATE' ,'UPDATED_BY','UPDATED_DATE'])

    return all_data



def Fetch_File_Name(uid):
    # uid = 1
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    file_name = cur.execute('''select FILE_NAME from KEWORDS WHERE KID=?''',(uid,))
    file_name = file_name.fetchall()
    file_name = pd.DataFrame(file_name, columns=['FILE_NAME'])
    file_name = file_name['FILE_NAME']

    return file_name


"""
This function to Fetch label name to fill them in the dropdown list 
:return list of label names
"""
def Fetch_Lable_Keywords(file_name):
    # file_name = "MASTER"
    # with sqlite3.connect(db_path) as cur:
    # Create a Connection
    conn, cur = createConnection()
    if file_name == 'MASTER':
        # print(len(file_name))
        label= cur.execute('''select DISTINCT LABEL from KEWORDS WHERE FILE_NAME=?''',(file_name,))

    if file_name == "PAYROLL":
        label = cur.execute('''select DISTINCT LABEL from KEWORDS WHERE FILE_NAME=?''', (file_name,))
    label = label.fetchall()
    label = pd.DataFrame(label, columns=['LABEL'])

    # for ind in label.index:
    #     print(label['LABEL'][ind], label['LABEL'][ind])
    # label = label.values.tolist()
    return label



def Check_No_Duplicate_Keyword(label,mkeyword,file_name):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    data = cur.execute('''select KEYWORD,LABEL,FILE_NAME from KEWORDS WHERE KEYWORD=? AND FILE_NAME=?''',(mkeyword,file_name))
    data = data.fetchall()
    duplicate_keyword = pd.DataFrame(data,columns=[ 'KEYWORD', 'LABEL','FILE_NAME'])
    # duplicate_keyword = data[(data['KEYWORD'] == mkeyword) & (data['LABEL'] == label)]
    return duplicate_keyword





"""
This function to add new keywords 
:param: receive the selected label and entered keyword from forms
:param select_label: string -> describtion about variable  
:return a df this dataframe will have data if the added keyword already exists and empty if added keyword is successful and no duplicate
"""
def Insert_Data_Keywords(select_label,kname,fname):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    mkeyword = kname.upper()
    mkeyword = mkeyword.replace(" ", "")
    label = select_label.upper()
    file_name = fname.upper()
    created_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    created_by = current_user.username

    #fetch data if it is already exist in KEWORDS table
    duplicate_keyword = Check_No_Duplicate_Keyword(label,mkeyword,file_name)

    if not duplicate_keyword.empty:
        validate = 'duplicate'
        return validate
    else:
        # validate = is_valid_input(mkeyword)

        if not is_valid_input(mkeyword):
            validate = 'invalid'
        else:
            mkeyword = sanitize_input(mkeyword)
            cur.execute("insert into KEWORDS(KEYWORD,LABEL,FILE_NAME,CREATED_DATE,CREATED_BY) values (?,?,?,?,?)",(mkeyword, label,file_name,created_date,created_by))
            conn.commit()
            conn.close()
            validate = 'True'
        return validate


"""
This function to Fetch current keyword and label name 
:return list of label names
"""
def Fetch_Current_Values(uid):

    # with sqlite3.connect(db_path) as cur:
        #uid = 2
    conn, cur = createConnection()
    # Fetch Current Label
    current_label= cur.execute('''select LABEL from KEWORDS WHERE KID=?''',(uid,))
    current_label = current_label.fetchall()
    current_label = pd.DataFrame(current_label, columns=['LABEL'])


    #Fetch Current Keyword
    current_keyword = cur.execute('''select KEYWORD from KEWORDS WHERE KID=?''', (uid,))
    current_keyword = current_keyword.fetchall()
    current_keyword = pd.DataFrame(current_keyword, columns=['KEYWORD'])
    current_keyword = current_keyword['KEYWORD'][0]

    #Fetch current file name
    file_name = cur.execute('''select FILE_NAME from KEWORDS WHERE KID=?''', (uid,))
    file_name = file_name.fetchall()
    file_name = pd.DataFrame(file_name, columns=['FILE_NAME'])
    file_name = file_name['FILE_NAME'][0]

    return file_name,current_label,current_keyword



def Edit_Keywords(select_label, kname,uid,file_name):

    select_label = select_label.upper()
    kname = kname.upper()
    file_name = file_name.upper()
    # with sqlite3.connect(db_path) as cur:

    updated_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = current_user.username
    # fetch data if it is already exist in KEWORDS table
    duplicate_keyword = Check_No_Duplicate_Keyword(select_label, kname,file_name)

    # if not duplicate_keyword.empty:
    #     return duplicate_keyword
    # else:
    #     cur.execute("update KEWORDS set KEYWORD=?,LABEL=?, FILE_NAME=?, UPDATED_BY=?,UPDATED_DATE=? where KID=?", (kname, select_label, file_name, updated_by,updated_date,uid))
    #     cur.commit()
    #     return duplicate_keyword
    if not duplicate_keyword.empty:
        validate = 'duplicate'
        return validate
    else:
        if not is_valid_input(kname):
            validate = 'invalid'
        else:
            kname = sanitize_input(kname)
            conn, cur = createConnection()
            cur.execute("update KEWORDS set KEYWORD=?,LABEL=?, FILE_NAME=?, UPDATED_BY=?,UPDATED_DATE=? where KID=?", (kname, select_label, file_name, updated_by,updated_date,uid))
            conn.commit()
            conn.close()
            validate = 'True'
        return validate


def Delete_Keywords(uid):
    # with sqlite3.connect(db_path) as cur:
    conn, cur = createConnection()
    cur.execute("delete from KEWORDS where KID=?", (uid,))
    conn.commit()
    conn.close()

def Fetch_keywords(column,filename):
    # column = 'CPR_NO'
    # with sqlite3.connect(db_path) as cur:
        #uid = 2
    conn, cur = createConnection()
    # Fetch Current Label
    keywords = cur.execute('''select KEYWORD from KEWORDS WHERE LABEL=? AND FILE_NAME=?''',(column,filename))
    keywords = keywords.fetchall()
    keywords = pd.DataFrame(keywords, columns=['KEYWORD'])
    keywords = keywords['KEYWORD'].values.tolist()

    return keywords

def Fetch_keywords_Without_Label(filename):
    # FILE_NAME = 'CPR_NO'
    # with sqlite3.connect(db_path) as cur:
        #uid = 2
    conn, cur = createConnection()
    # Fetch Current Label
    keywords = cur.execute('''select KEYWORD from KEWORDS WHERE FILE_NAME=?''',(filename,))
    keywords = keywords.fetchall()
    keywords = pd.DataFrame(keywords, columns=['KEYWORD'])
    keywords = keywords['KEYWORD'].values.tolist()

    return keywords





