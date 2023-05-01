"""
Filename: application\Control_Panel\keywords_db_Queries1.py

The filename is "keywords_db_Queries1.py" and it is located in the "application/Control_Panel" directory. The purpose of this file is to contain functions that interact with the database to fetch, insert, edit, or delete keywords.

The file depends on the "keywords" module, which contains functions to interact with the database. The version of this module is not specified in the code.



"""

from ..models import keywords
from flask_login import  current_user

"""
This function to Fetch all keywords based on the selected label 
:return all keywords df
"""
def Fetch_All_keywords(File_name, Label):
    all_data = system_keywords.Fetch_All_keywords_by_File_Name_And_Labels_dataframe(File_name, Label)
    return all_data



def Fetch_File_Name(uid):
    file_name = system_keywords.Fetch_File_Name_by_Id(uid)

    return file_name


"""
This function to Fetch label name to fill them in the dropdown list
:return list of label names
"""
def Fetch_Lable_keywords(file_name):
    labels = system_keywords.Fetch_All_labels_by_File_Name_dataframe(file_name)
    return labels




# """
# This function to Fetch current keyword and label name
# :return list of label names
# """
def Fetch_Current_Values(uid):
    # Fetch Current Keyword
    result = system_keywords.Fetch_all_label_by_kid_dataframe(uid)
    rows = result.fetchall()

    current_label = rows[0][0]
    current_keyword = rows[0][1]
    file_name = rows[0][2]
    return file_name,current_label,current_keyword



def Edit_keywords(select_label, kname,uid,file_name):
    updated_by = current_user.username
    validate = system_keywords.Update_keyword_by_id(uid,kname, select_label, file_name,updated_by)
    return validate


def Delete_keywords(uid):
    delete_msg = system_keywords.Delete_Keyword_by_Id(uid)


"""
This function to add new keywords
:param: receive the selected label and entered keyword from forms
:param select_label: string -> describtion about variable
:return a df this dataframe will have data if the added keyword already exists and empty if added keyword is successful and no duplicate
"""
def Insert_Data_keywords(select_label,kname,fname):
    created_by = current_user.username
    #fetch data if it is already exist in KEWORDS table
    check_msg = system_keywords.Add_Keyword_check_not_exist(kname, select_label, fname,created_by)

    return check_msg


def Fetch_keywords_with_lable(column,filename):
    keywords = system_keywords.Fetch_keyword_by_File_Name_and_Label_list(filename, column)
    return keywords

def Fetch_keywords_Without_Label(filename):
    keywords = system_keywords.Fetch_keyword_by_File_Name_list(filename)
    return keywords

# def Check_No_Duplicate_Keyword(label,mkeyword,file_name):
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     data = cur.execute('''select KEYWORD,LABEL,FILE_NAME from KEWORDS WHERE KEYWORD=? AND FILE_NAME=?''',(mkeyword,file_name))
#     data = data.fetchall()
#     duplicate_keyword = pd.DataFrame(data,columns=[ 'KEYWORD', 'LABEL','FILE_NAME'])
#     # duplicate_keyword = data[(data['KEYWORD'] == mkeyword) & (data['LABEL'] == label)]
#     return duplicate_keyword







# """
# This function to Fetch current keyword and label name
# :return list of label names
# """
# def Fetch_Current_Values(uid):

#     # with sqlite3.connect(db_path) as cur:
#         #uid = 2
#     conn, cur = createConnection()
#     # Fetch Current Label
#     current_label= cur.execute('''select LABEL from KEWORDS WHERE KID=?''',(uid,))
#     current_label = current_label.fetchall()
#     current_label = pd.DataFrame(current_label, columns=['LABEL'])

#     # Fetch Current Keyword
#     result = cur.execute('''select LABEL, KEYWORD, FILE_NAME from KEWORDS WHERE KID=?''', (uid,))
#     rows = result.fetchall()

#     # current_label = rows[0][0]
#     current_keyword = rows[0][1]
#     print(current_keyword)
#     file_name = rows[0][2]
#     print(file_name)

#     return file_name,current_label,current_keyword



# def Edit_keywords(select_label, kname,uid,file_name):

#     select_label = select_label.upper()
#     kname = kname.upper()
#     file_name = file_name.upper()
#     # with sqlite3.connect(db_path) as cur:

#     updated_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
#     updated_by = current_user.username
#     # fetch data if it is already exist in KEWORDS table
#     duplicate_keyword = Check_No_Duplicate_Keyword(select_label, kname,file_name)

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


# def Delete_keywords(uid):
#     # with sqlite3.connect(db_path) as cur:
#     conn, cur = createConnection()
#     cur.execute("delete from KEWORDS where KID=?", (uid,))
#     conn.commit()
#     conn.close()

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

# #     return keywords
# def Fetch_keywords(column=None, filename=None):
#     conn, cur = createConnection()

#     if column and filename:
#         # Fetch keywords with given label and filename
#         keywords = cur.execute('''SELECT KEYWORD FROM KEWORDS WHERE LABEL=? AND FILE_NAME=?''', (column, filename))
#     elif filename:
#         # Fetch all keywords for given filename
#         keywords = cur.execute('''SELECT KEYWORD FROM KEWORDS WHERE FILE_NAME=?''', (filename,))

#     keywords = [row[0] for row in keywords.fetchall()]
#     conn.close()

#     return keywords




