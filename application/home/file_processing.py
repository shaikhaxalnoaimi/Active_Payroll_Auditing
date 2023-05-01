"""
Filename:application\home\file_processing.py

Purpose: This file contains functions for handling file uploads, reading and formatting data from uploaded files, and comparing uploaded files with previously uploaded files.

Dependencies:

datetime module
werkzeug.utils module
flask_login module
os module
glob module
pandas module
Fetch_Keywords function from keywords_db_Queries.py module
app instance from app.py module


Code structure:

get_uploads_folder(folder_name): function to get the path of the folder where uploaded files will be stored
generate_file_name(file_name, extension): function to generate a unique filename for uploaded files
read_file(f): function to read an uploaded file and return a pandas dataframe
Initial_Formating(new_file): function to format column names in a pandas dataframe
dateFormatting(new_file): function to format date columns in a pandas dataframe
setFileName(folder_name): function to set the filename based on the folder name
Confirm_conflict(new,folder_name): function to check for conflicts in column names in an uploaded file
Remove_Conflict(new, approved_columns,folder_name): function to remove conflicting columns from an uploaded file
Cleaning_Prepar_df(new,approved_columns,folder_name): function to clean and prepare an uploaded file for validation
InitialValidatFile(new,folder_name,approved_columns): function to validate an uploaded file and compare it with previously uploaded files

"""


from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import current_user
import os
import glob
import pandas as pd
from app import app

#eg. folder name = master_data
from application.Control_Panel.keywords_db_Queries import Fetch_keywords_Without_Label,Fetch_keywords_with_lable


def get_uploads_folder(folder_name):
    user_path = current_user.username
    path = os.path.join(
        app.root_path, "data", folder_name, user_path
    )
    isdir = os.path.isdir(path)
    # if golder not exist create new one
    if not isdir:
        os.makedirs(path)

    return path


# Generate file name as the following
#eg. filename = Master
def generate_file_name(file_name, extension):
    t = datetime.now()
    n =  file_name +"-"+ t.strftime("%d%m%Y %H%M%S")+ extension
    filename = secure_filename(n)
    return filename



#read the uploaded file
def read_file(f):
    df = pd.read_excel(f)
    return df

# def read_file_multilple_sheet(f):
#
#
#
#
#     # return sheet_to_df_map

def read(f):
    # path = repr(f)
    df = pd.read_excel(f)
    return df

def Initial_Formating(new_file):
    new_file.columns = new_file.columns.str.replace(' ', '')
    new_file.columns = new_file.columns.str.upper()
    new_file = new_file.loc[:, ~new_file.columns.duplicated()].copy()
    # new_file = new_file.drop(['HOLDREGULAR_OVERTIME'], axis=1, errors='ignore')
    # new_file = new_file.drop(['Hold REGULAR_OVERTIME'], axis=1, errors='ignore')
    return new_file


def dateFormatting(new_file):
    ##### Preprocess Date ########
    # new_file = pd.read_excel(r'C:\nao-payroll-deployment-dock\NAO-Payroll\application\data\master_data\admin\Database_Jan_2021-_S_-_OvertimeTesting-05112022_150346.xlsx')

    for column in new_file.columns:
        if 'DATE_OF_BIRTH' in column:
            # new_file['DATE_OF_BIRTH'].astype(str).str.isdigit()
            new_file['DATE_OF_BIRTH'] = pd.to_datetime(new_file['DATE_OF_BIRTH'], errors='coerce')
            # print(new_file['DATE_OF_BIRTH'])
            # new['DATE_OF_BIRTH'].replace(pd.NaT, '',inplace=True)
            # new['DATE_OF_BIRTH'] = new['DATE_OF_BIRTH'].dropna()
            end = pd.to_datetime('2222-02-22') # if date is Nat Replace it with 2222-02-22 (becuase Nat is not supported formate)
            new_file['DATE_OF_BIRTH'] = new_file['DATE_OF_BIRTH'].fillna(end)
            new_file['DATE_OF_BIRTH'] = pd.to_datetime(new_file.DATE_OF_BIRTH).dt.tz_localize(None)

    return new_file


def setFileName(folder_name):
    # Fetch columns from uploaded file (new) that match keyword in db
    if folder_name == "master_data":
        file_name = "MASTER"  # to fetch all keywords and label related to the master file in db
    elif folder_name == "MonthlyPayroll_data":
        file_name = "PAYROLL"  # to fetch all keywords and label related to the master file in db

    return file_name


def Confirm_conflict(new,folder_name):
    # new= pd.read_excel('C:/Users/admin/Desktop/Payroll Data for test/Master -1 - conflict with missing columns.xlsx')
    new = Initial_Formating(new)

    # file_name ='MASTER'
    file_name = setFileName(folder_name)
    # (file_name)
    global conflict_list,different,duplicate_cols
    conflict_list = []
    different = ''

    match_cols = []
    # for column in new.columns:
    keys = Fetch_keywords_Without_Label(filename=file_name)
    new = new.loc[:, new.columns.notna()]
    for key in keys:
        match_cols.append([col for col in new.columns if key in col])

    # Fetch columns that has conflict in column name such as social, social_pfc
    duplicate_cols = []
    for match_col in match_cols:
        # if len(match_col) > 1:
        if len(match_col) > 1:
            duplicate_cols.append(match_col)

    if duplicate_cols:
        different = 'Conflict'
        conflict_list = duplicate_cols

    return different, conflict_list,new


def Remove_Conflict(new, approved_columns,folder_name):
    # new= pd.read_excel('C:/Users/admin/Desktop/Payroll Data for test/Master -1 - conflict with missing columns.xlsx')
    # approved_columns = ['GRADE', 'SOCIAL', 'NATIONALITY', 'NAME', 'POSITION']
    new = Initial_Formating(new)
    # file_name = "MASTER"
    # (approved_columns)
    file_name = setFileName(folder_name)
    match_cols = []
    # for column in new.columns:
    keys = Fetch_keywords_Without_Label(filename=file_name)
    for key in keys:
        match_cols.append([col for col in new.columns if key in col])

    # Fetch columns that has conflict in column name such as social, social_pfc
    duplicate_cols = []
    for match_col in match_cols:
        if len(match_col) > 1:
            duplicate_cols.append(match_col)

    # duplicate_cols = [['APPROVED_GRADE', 'GRADE'], ['SOCIAL', 'SOCIAL_PFC']]
    # approved_columns = ['GRADE', 'SOCIAL']
    # Fetch and remove relevant column and keep not relevant
    not_relevant_cols = []
    for i in range(len(duplicate_cols)):
        for j in duplicate_cols[i]:
            if (j != approved_columns[i]):
                not_relevant_cols.append(j)

    # Drop not relevant and conflict columns from new uploaded file
    for not_relevant_col in not_relevant_cols:
        new = new.drop([not_relevant_col], axis=1,errors='ignore')

    # (new.columns)
    return new

"""
Call function to return confirmed conflict variables
"""
def Cleaning_Prepar_df(new,approved_columns,folder_name):
    # (approved_columns)
    # (folder_name)

    different, conflict_list,new = Confirm_conflict(new,folder_name)

    """
     if there are conflict columns name return pop up to ask end user to confirm whitch columns correct 
    """
    # if conflict_list and not approved_columns:
    #     # check if there is a conflict (duplication in substring column name) then return pop up the the end user
    #     return new, [], conflict_list, [], different

    if approved_columns and conflict_list:
        new = Remove_Conflict(new, approved_columns,folder_name)
        # (new.columns)

    # set file if it is master or payroll based on folder_name
    file_name = setFileName(folder_name)

    # set the required columns names based on file_name
    if file_name == "MASTER":
        # List of all standard columns
        ColmunsList = ['CPR_NO', 'EMPLOYEE_NAME', 'HIRE_DATE', 'POSITION_TITLE', 'ACCOUNTNO',
                       'ANNUAL', 'SICK', 'DATE_OF_BIRTH',
                        'MARITAL_STATUS',
                       'GRADE','NATIONALITY','DIRECTORATE','CATEGORY']
    elif file_name == "PAYROLL":
        ColmunsList = ['CAR_ALLOW', 'TRANSPORT_ALLOW', 'COMMUNICATION_ALLOW', 'LIVING_STD_ALLOW',
                       'SOCIAL_ALLOW', 'HOUSING_ALLOW', 'SPECIAL_ALLOW', 'SOCIAL_PEN_FUND_CONTRIP_DED',
                       'PENSION_FUND_CONTRIPUTION_DED', 'REGULAR_OVERTIME', 'HOLIDAY_OVERTIME',
                       'UNEMPLOYMENT_INSUR_DED', 'CPR_NO','HOLIDAY_OT_HOURS','REGULAR_OT_HOURS','BASIC_SALARY']


    # Rename any column that contains the any of keywords based on label such as LABEL:CPR_NO, KEYWORDS:CPR,CPRNO,EMPLOYE_NO,EMPLOYEE_ID,CPR_NUMBER
    # approved_columns = ['GRADE','SOCIAL']
    # new= pd.read_excel('C:/Users/admin/Desktop/Payroll Data for test/payroll.xlsx')
    # new = Initial_Formating(new)
    #
    # # folder_name = "master_data"
    # file_name = "PAYROLL"

    for column in ColmunsList:
        # (column)
        keys = Fetch_keywords_with_lable(column, file_name)
        # Rename the columns based on keywords
        new = new.rename(lambda x: column if any(k in x for k in keys) else x, axis=1)

    # Fetch the required columns from the uploaded file (new)
    def asset_filter(tag_n):
        tags = tag_n.split()  # common delimeter is "space"
        tags = [t for t in tags if len([a for a in ColmunsList if t.startswith(a)]) >= 1]
        # (tags)
        return tags  # can " ".join(tags) if str type is desired

    # send the column of the upload file (new) to function to arrange them in a list of list it is required to decide which column not in index
    list_columns = []
    for column in new.columns:
        list_columns.append(asset_filter(column))



    # Remove empty List from List
    cleaned_cols = [cleaned_cols for cleaned_cols in list_columns if cleaned_cols != []]


    # (cleaned_cols)
    # Convert list of list to list
    def flatten(l):
        return [item for sublist in l for item in sublist]

    cleaned_cols = flatten(cleaned_cols)


    # fitch the required columns from uploaded df and then check if it is match with the keyword in db if yes add them in df  and exsit the loop of the keyword
    coulmns_in_uploaded_file = []
    # (cleaned_cols)
    for column in cleaned_cols:
        keys = Fetch_keywords_with_lable(column, file_name)
        # (keys)
        # (column)
        for key in keys:
            if column == key:
                # ("-------")
                # (key)
                # (column)
                coulmns_in_uploaded_file.append(column)
                break
    # (coulmns_in_uploaded_file)
    # we got a list of all columns names match withg the stored keyword in df
    # filter them by comparing them with the standred columns to know which column is missing
    # if column in coulmns_in_uploaded_file not match with ColmunsList

    coulmns_not_in_uploaded_file = []
    for ColmunsListSatnd in ColmunsList:
        if ColmunsListSatnd not in coulmns_in_uploaded_file:
            coulmns_not_in_uploaded_file.append(ColmunsListSatnd)
    # (new)
    return new, coulmns_not_in_uploaded_file,conflict_list, ColmunsList,different



# compare between last and current uploaded file
def InitialValidatFile(new,folder_name,approved_columns):
    global different, notMatchColumn
    # different = ''
    # notMatchColumn = False

    if folder_name == 'master_data':
        # new= pd.read_excel('C:/Users/admin/Desktop/Payroll Data for test/Master -1 - Copy.xlsx')
        new, coulmns_not_in_uploaded_file,conflict_columns, ColmunsList,different = Cleaning_Prepar_df(new,approved_columns,folder_name)
        new = dateFormatting(new)
    elif folder_name == "MonthlyPayroll_data":
        new, coulmns_not_in_uploaded_file,conflict_columns, ColmunsList,different = Cleaning_Prepar_df(new,approved_columns,folder_name)







    if conflict_list and not approved_columns:
        return different, conflict_columns, coulmns_not_in_uploaded_file,new
    """
    if columns not in uploaded file then check if it include columns that are not mandatory return confirmation to the end user else return theses columns to notify the end user
    """
    if coulmns_not_in_uploaded_file:
        # print(coulmns_not_in_uploaded_file)
        different = 'MissingColumns'
        return different,[], coulmns_not_in_uploaded_file,new

    # filter by column name
    new = new[ColmunsList]
     # convert list to df
    AcceptedColumns = pd.DataFrame(ColmunsList)

    # set valid columns  and received file columns
    df1_columns = set(AcceptedColumns[0])
    df2_columns = set(new.columns)

    # if columns match accept  file if not rejected
    if df1_columns == df2_columns:
        # Get last file to make sure this file didnt uploaded before
        folder_path = get_uploads_folder(folder_name)
        file_type = r'/*.xlsx'
        files = glob.glob(folder_path + file_type)
        # files = glob.glob(folder_path + "/*.xlsx")
        if files:
            # read file and check with new file
            for file in files:
                last = read(file)
                try:
                    # filter by column name
                    last = last[ColmunsList]
                except ValueError:
                    ("Element not in list !")

                if last.equals(new):
                    ## the master sheet uploaded are  match the pervious file so rejected and show correct messgae
                    different = 'exists' # same content
                    break
                else:
                    ## the master sheet uploaded are not match the pervious file content and pass the colmun names test so accepted
                    different = True  # different content
        else:
            ## the master sheet uploaded for the first time so it will not compared with other sheet but pass the colmun names test so accepted
            different = True

    else:
        ## the master sheet uploaded dosnt pass the colmun names test so rejected
        different = False  # reject (different column)
    new = dateFormatting(new)
    return different, [],[], new

