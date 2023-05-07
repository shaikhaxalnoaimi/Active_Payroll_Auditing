"""
Filename: application\Control_Panel\keywords_db_Queries.py

Purpose: This file contains functions to interact with the KEWORDS table in the database. It allows for the creation of the table, insertion, deletion, and editing of keywords, as well as fetching data from the table.

Dependencies:

sqlite3 (built-in)
pandas (version 1.2.4)
flask_login (version 0.5.0)
datetime (built-in)
application.Control_Panel.validation (custom module)
Code structure:

createConnection(): function to create a connection to the database
Create_Tables(): function to create the KEWORDS table in the database
Fetch_All_Keywords(file_name, selected_value): function to fetch all keywords based on the selected label
Fetch_File_Name(uid): function to fetch the file name for a given keyword ID
Fetch_Lable_Keywords(file_name): function to fetch label names for a given file name
Check_No_Duplicate_Keyword(label,mkeyword,file_name): function to check if a keyword already exists in the KEWORDS table
Insert_Data_Keywords(select_label,kname,fname): function to insert a new keyword into the KEWORDS table
Fetch_Current_Values(uid): function to fetch the current keyword and label name for a given keyword ID
Edit_Keywords(select_label, kname,uid,file_name): function to edit a keyword in the KEWORDS table
Delete_Keywords(uid): function to delete a keyword from the KEWORDS table
Fetch_Keywords(column=None, filename=None): function to fetch keywords from the KEWORDS table based on label and/or file name.
"""

import sqlite3

import pandas as pd
from flask_login import current_user
from datetime import datetime
from application import db_path, db
from application.Control_Panel.validation import is_valid_input, sanitize_input
from application.models import keywords


def Fetch_Lable_Keywords(file_name):
    """
    This function to Fetch label name to fill them in the dropdown list
    :return list of label names
    """
    # Execute the query and save the results to a list of tuples
    results = keywords.Fetch_All_labels_by_File_Name_dataframe(file_name)
    return results


def Fetch_All_Keywords(File_name, Label):
    all_data = keywords.Fetch_All_keywords_by_File_Name_And_Labels_dataframe(File_name, Label)
    return all_data


def Fetch_Current_Values(uid):
    # Fetch Current Keyword
    result = keywords.Fetch_all_label_by_kid_dataframe(uid)
    current_label = result.LABEL
    current_keyword = result.KEYWORD
    file_name = result.FILE_NAME
    return file_name, current_label, current_keyword


def Edit_Keywords(select_label, kname, uid, file_name):
    updated_by = current_user.username
    validate = keywords.Update_keyword_by_id(uid, kname, select_label, file_name, updated_by)
    return validate


def Delete_Keywords(uid):
    delete_msg = keywords.Delete_Keyword_by_Id(uid)


def Insert_Data_Keywords(select_label, kname, fname):
    created_by = current_user.username
    # fetch data if it is already exist in keywords table

    # new = keywords("keywork", select_label, fname, created_by, "test")
    # db.session.add(new)
    # db.session.commit()

    check_msg = keywords.Add_Keyword_check_not_exist(kname, select_label, fname, created_by)
    # check_msg = ""
    return check_msg

#
# def createConnection():
#     # connect to the database with a limited user
#     conn = sqlite3.connect(db_path, isolation_level=None)
#     cur = conn.cursor()
#     # cur.execute("PRAGMA query_only = 1")
#
#     return conn, cur
#
#
# """
# This function to Fetch all keywords based on the selected label
# :return all keywords df
# """
# # def Fetch_All_Keywords(file_name, selected_value):
# #     query = 'SELECT KID, FILE_NAME, LABEL, KEYWORD, CREATED_BY, CREATED_DATE, UPDATED_BY, UPDATED_DATE FROM KEWORDS WHERE LABEL=? AND FILE_NAME=?'
# #     conn, cur = createConnection()
# #     all_data = cur.execute(query, (selected_value, file_name)).fetchall()
# #     columns = ['KID', 'FILE_NAME', 'LABEL', 'KEYWORD', 'CREATED_BY', 'CREATED_DATE', 'UPDATED_BY', 'UPDATED_DATE']
# #     all_data = pd.DataFrame(all_data, columns=columns)
# #     conn.close()
# #     return all_data
#
#
#
# def Fetch_File_Name(uid):
#     # uid = 1
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     file_name = cur.execute('''select FILE_NAME from KEWORDS WHERE KID=?''',(uid,))
#     file_name = file_name.fetchall()
#     file_name = pd.DataFrame(file_name, columns=['FILE_NAME'])
#     file_name = file_name['FILE_NAME']
#
#     return file_name
#
#
#
#
#
# def Check_No_Duplicate_Keyword(label,mkeyword,file_name):
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     data = cur.execute('''select KEYWORD,LABEL,FILE_NAME from KEWORDS WHERE KEYWORD=? AND FILE_NAME=?''',(mkeyword,file_name))
#     data = data.fetchall()
#     duplicate_keyword = pd.DataFrame(data,columns=[ 'KEYWORD', 'LABEL','FILE_NAME'])
#     # duplicate_keyword = data[(data['KEYWORD'] == mkeyword) & (data['LABEL'] == label)]
#     return duplicate_keyword
#
#
#
#
#
# """
# This function to add new keywords
# :param: receive the selected label and entered keyword from forms
# :param select_label: string -> describtion about variable
# :return a df this dataframe will have data if the added keyword already exists and empty if added keyword is successful and no duplicate
# """
# def Insert_Data_Keywords(select_label,kname,fname):
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     mkeyword = kname.upper()
#     mkeyword = mkeyword.replace(" ", "")
#     label = select_label.upper()
#     file_name = fname.upper()
#     created_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#     created_by = current_user.username
#
#     #fetch data if it is already exist in KEWORDS table
#     duplicate_keyword = Check_No_Duplicate_Keyword(label,mkeyword,file_name)
#
#     if not duplicate_keyword.empty:
#         validate = 'duplicate'
#         return validate
#     else:
#         # validate = is_valid_input(mkeyword)
#
#         if not is_valid_input(mkeyword):
#             validate = 'invalid'
#         else:
#             mkeyword = sanitize_input(kname)
#             cur.execute("insert into KEWORDS(KEYWORD,LABEL,FILE_NAME,CREATED_DATE,CREATED_BY) values (?,?,?,?,?)",(mkeyword, label,file_name,created_date,created_by))
#             conn.commit()
#             conn.close()
#             validate = 'True'
#         return validate
#
#
# """
# This function to Fetch current keyword and label name
# :return list of label names
# """
# def Fetch_Current_Values(uid):
#
#     # with sqlite3.connect(db_path) as cur:
#         #uid = 2
#     conn, cur = createConnection()
#     # Fetch Current Label
#     current_label= cur.execute('''select LABEL from KEWORDS WHERE KID=?''',(uid,))
#     current_label = current_label.fetchall()
#     current_label = pd.DataFrame(current_label, columns=['LABEL'])
#
#     # Fetch Current Keyword
#     result = cur.execute('''select LABEL, KEYWORD, FILE_NAME from KEWORDS WHERE KID=?''', (uid,))
#     rows = result.fetchall()
#
#     # current_label = rows[0][0]
#     current_keyword = rows[0][1]
#     print(current_keyword)
#     file_name = rows[0][2]
#     print(file_name)
#
#     return file_name,current_label,current_keyword
#
#
#
# def Edit_Keywords(select_label, kname,uid,file_name):
#
#     select_label = select_label.upper()
#     kname = kname.upper()
#     file_name = file_name.upper()
#     # with sqlite3.connect(db_path) as cur:
#
#     updated_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#     updated_by = current_user.username
#     # fetch data if it is already exist in KEWORDS table
#     duplicate_keyword = Check_No_Duplicate_Keyword(select_label, kname,file_name)
#
#     # if not duplicate_keyword.empty:
#     #     return duplicate_keyword
#     # else:
#     #     cur.execute("update KEWORDS set KEYWORD=?,LABEL=?, FILE_NAME=?, UPDATED_BY=?,UPDATED_DATE=? where KID=?", (kname, select_label, file_name, updated_by,updated_date,uid))
#     #     cur.commit()
#     #     return duplicate_keyword
#     if not duplicate_keyword.empty:
#         validate = 'duplicate'
#         return validate
#     else:
#         if not is_valid_input(kname):
#             validate = 'invalid'
#         else:
#             kname = sanitize_input(kname)
#             conn, cur = createConnection()
#             cur.execute("update KEWORDS set KEYWORD=?,LABEL=?, FILE_NAME=?, UPDATED_BY=?,UPDATED_DATE=? where KID=?", (kname, select_label, file_name, updated_by,updated_date,uid))
#             conn.commit()
#             conn.close()
#             validate = 'True'
#         return validate
#
#
# def Delete_Keywords(uid):
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     cur.execute("delete from KEWORDS where KID=?", (uid,))
#     conn.commit()
#     conn.close()
#
# # def Fetch_keywords(column,filename):
# #     # column = 'CPR_NO'
# #     # with sqlite3.connect(db_path) as cur:
# #         #uid = 2
# #     conn, cur = createConnection()
# #     # Fetch Current Label
# #     keywords = cur.execute('''select KEYWORD from KEWORDS WHERE LABEL=? AND FILE_NAME=?''',(column,filename))
# #     keywords = keywords.fetchall()
# #     keywords = pd.DataFrame(keywords, columns=['KEYWORD'])
# #     keywords = keywords['KEYWORD'].values.tolist()
# #
# #     return keywords
# #
# # def Fetch_keywords_Without_Label(filename):
# #     # FILE_NAME = 'CPR_NO'
# #     # with sqlite3.connect(db_path) as cur:
# #         #uid = 2
# #     conn, cur = createConnection()
# #     # Fetch Current Label
# #     keywords = cur.execute('''select KEYWORD from KEWORDS WHERE FILE_NAME=?''',(filename,))
# #     keywords = keywords.fetchall()
# #     keywords = pd.DataFrame(keywords, columns=['KEYWORD'])
# #     keywords = keywords['KEYWORD'].values.tolist()
#
# #     return keywords
# def Fetch_Keywords(column=None, filename=None):
#     conn, cur = createConnection()
#
#     if column and filename:
#         # Fetch keywords with given label and filename
#         keywords = cur.execute('''SELECT KEYWORD FROM KEWORDS WHERE LABEL=? AND FILE_NAME=?''', (column, filename))
#     elif filename:
#         # Fetch all keywords for given filename
#         keywords = cur.execute('''SELECT KEYWORD FROM KEWORDS WHERE FILE_NAME=?''', (filename,))
#
#     keywords = [row[0] for row in keywords.fetchall()]
#     conn.close()
#
#     return keywords
#
#
#
#
