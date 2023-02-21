import glob
import os
import pandas as pd
from flask_login import current_user
from flask import session
from application.home.file_processing import get_uploads_folder, generate_file_name, read_file, \
    InitialValidatFile, Initial_Formating, dateFormatting


######################################################################################-->
######################### Process uploaded master sheet ##############################-->
######################################################################################-->
def process_master_form(form):
    f = form.master.data
    file_name = f.filename.split('.')[0]
    # current_path = os.path.abspath(file_name)
    extension = os.path.splitext(f.filename)[1]
    session['extension'+ str(current_user.username)] = extension
    path = get_uploads_folder("master_data")
    session['path'+ str(current_user.username)] = path
    # this process
    filename = generate_file_name(str(file_name), extension)
    session['file_name'+ str(current_user.username)] = filename
    folderName = "master_data"

    new_file = read_file(f)
    new_file = Initial_Formating(new_file)
    new_file = dateFormatting(new_file)
    # print(new_file)

    approved_columns = [] # this will be empty becuase in intitial validation file we still didnt know if there is an conflict columns or not
    different, conflict_list, coulmns_not_in_uploaded_file,new =  InitialValidatFile(new_file,folderName,approved_columns)
    # print(different)
    if different == True:
        created_path = path+'/'+ filename
        new.to_excel(created_path, index=False)
        success = 'success'
        return success,[],[],pd.DataFrame()
    elif  different == 'exists':
        exists = 'exists'
        return exists,[],[],pd.DataFrame()
    elif different == 'MissingColumns':
        return different, [], coulmns_not_in_uploaded_file,''  # incorrect columns names to notify end users
    elif different == 'Conflict':
        return different, conflict_list,[], new
    else:
        incorrect = 'incorrect'
        return incorrect,[],[],pd.DataFrame()


######################################################################################-->
##################### Process uploaded overtime payroll sheet #######################-->
######################################################################################-->
# def processPayrollForm(form):
#     # the approved file
#     f = form.PayRoll.data
#     file_name = f.filename.split('.')[0]
#     # current_path = os.path.abspath(file_name)
#     extension = os.path.splitext(f.filename)[1]
#     session['extension' + str(current_user.username)] = extension
#     path = get_uploads_folder("MonthlyPayroll_data")
#     session['path' + str(current_user.username)] = path
#     # this process
#     filename = generate_file_name(str(file_name), extension)
#     session['file_name' + str(current_user.username)] = filename
#     folderName = "MonthlyPayroll_data"
#
#     new_file = read_file(f)
#     new_file = Initial_Formating(new_file)
#
#     approved_columns = []  # this will be empty becuase in intitial validation file we still didnt know if there is an conflict columns or not
#     different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,approved_columns)
#
#     # print(different)
#     if different == True:
#         created_path = path + '/' + filename
#         # print(created_path)
#         new.to_excel(created_path, index=False)
#         success = 'success'
#         return success, [], [], pd.DataFrame()
#     elif different == 'exists':
#         exists = 'exists'
#         return exists, [], [], pd.DataFrame()
#     elif different == 'MissingColumns':
#         return different, [], coulmns_not_in_uploaded_file, ''  # incorrect columns names to notify end users
#     elif different == 'Conflict':
#         return different, conflict_list, [], new
#     else:
#         incorrect = 'incorrect'
#         return incorrect, [], [], pd.DataFrame()




def processPayrollForm(form):
    # the approved file
    f = form.PayRoll.data
    file_name = f.filename.split('.')[0]
    # current_path = os.path.abspath(file_name)
    extension = os.path.splitext(f.filename)[1]
    session['extension' + str(current_user.username)] = extension
    path = get_uploads_folder("MonthlyPayroll_data")
    session['path' + str(current_user.username)] = path
    # this process
    filename = generate_file_name(str(file_name), extension)
    session['file_name' + str(current_user.username)] = filename
    folderName = "MonthlyPayroll_data"

    xls = pd.ExcelFile(f)

    # to read all sheets to a map
    sheet_to_df_map = {}
    for sheet_name in xls.sheet_names:
        sheet_to_df_map[sheet_name] = xls.parse(sheet_name)
        # you can also use sheet_index [0,1,2..] instead of sheet name.
    sucess_count = 0
    exists_count = 0
    for key in sheet_to_df_map:
        new_file = sheet_to_df_map[key]
        new_file = Initial_Formating(new_file)

        approved_columns = []  # this will be empty becuase in intitial validation file we still didnt know if there is an conflict columns or not
        different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,
                                                                                         approved_columns)

        # print(different)
        if different == True:
            sucess_count = sucess_count + 1
            created_path = path + '/' + key + '-' + filename
            # print(created_path)
            new.to_excel(created_path, index=False, sheet_name=key)
            if sucess_count == len(sheet_to_df_map):
                success = 'success'
                return success, [], [], pd.DataFrame(),''
        elif different == 'MissingColumns':
            return different, [], coulmns_not_in_uploaded_file, pd.DataFrame(),key  # incorrect columns names to notify end users
        elif different == 'Conflict':
            return different, conflict_list, [], new,''
    if different == 'exists':
        exists = 'exists'
        return exists, [], [], pd.DataFrame(),''
    else:
        incorrect = 'incorrect'
        return incorrect, [], [], pd.DataFrame(),key


"""
<-- ### Complete the Process of uploaded master sheet when confirm conflict columns#####-->
"""
def process_uploaded_df(uploaded_data, approved_columns,folderName):
    # Remove space from columns names
    # strip leading white spaces
    uploaded_data.columns = [c.lstrip() for c in uploaded_data]

    # strip trailing white spaces
    uploaded_data.columns = [c.rstrip() for c in uploaded_data]

    filename = session['file_name'+ str(current_user.username)] if 'file_name'+ str(current_user.username) in session else ""
    path = session['path'+ str(current_user.username)] if 'path'+ str(current_user.username) in session else ""

    # extension = session['extension'+ str(current_user.username)] if 'extension'+ str(current_user.username) in session else ""
    new_file = uploaded_data
    new_file = Initial_Formating(new_file)

    # this cleaning process only for master data
    if folderName == "master_data":
        new_file = dateFormatting(new_file)


    # print(approved_columns)
    different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file,folderName,approved_columns)

    # print(different)
    if different == True:
        # you can do the cleaning df here
        created_path = path+'/'+ filename
        new.to_excel(created_path, index=False)
        success = 'success'
        return success,[]
    elif  different == 'exists':
        exists = 'exists'
        return exists,[]
    elif different == 'MissingColumns':
        return different, coulmns_not_in_uploaded_file # incorrect columns names to notify end users
    else:
        incorrect = 'incorrect'
        return incorrect,[]


######################################################################################-->
############# Get all uploaded master files from folder master_data ##################-->
######################################################################################-->
def GetFileName(folderName):
    extension = 'xlsx'
    folderName = folderName
    path = get_uploads_folder(folderName)
    os.chdir(path)
    full_paths = []
    # print(files)
    files = [i for i in glob.glob('*.{}'.format(extension))]
    for file in files:
        path = str(path).replace(os.path.sep, '/')
        full_path = str(path)+'/' +str(file)
        full_paths.append(full_path)

    return full_paths,files

######################################################################################-->
##################### Auditing_Validation_Process ####################################-->
######################################################################################-->
"""
This function to check if there is a result from auditing or not 
:param data need to be checked such as duplicateName df 
:return set variable to False if no issues True if there is an issues
"""
def Check_Auditing_Validation(data):
    if data.empty:
        val = True
    else:
        val = False
    return val


######################################################################################-->
################## Handling (Living, Housing, and Social Allowance file) ##################-->
######################################################################################-->
"""
This function to check if there is a result from auditing or not 
:param data need to be checked such as duplicateName df 
:return set variable to False if no issues True if there is an issues
"""
# def Handel_Living_Housing_Social_Validation_File(data):
#     xls = pd.ExcelFile('path_to_file.xls')
#     df1 = pd.read_excel(xls, 'Sheet1')
#     df2 = pd.read_excel(xls, 'Sheet2')
