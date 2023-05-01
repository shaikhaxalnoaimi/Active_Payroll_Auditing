# """
# File Name: application\home\util.py
# The purpose of the code file is to handle the processing and validation of uploaded files in a web application.
#
# The code file has dependencies on the following libraries with their respective versions:
#
# pandas (version not specified)
# os (version not specified)
# glob (version not specified)
# xlsxwriter (version not specified)
# flask (version not specified)
# flask_login (version not specified)
# The code structure includes multiple functions for processing and validating uploaded files, such as:
#
# initilizePayrollFormVariable(): initializes variables for processing uploaded payroll files
# Initial_Formating(): performs initial formatting on a dataframe
# InitialValidatFile(): performs initial validation on a dataframe
# process_uploaded_payroll(): processes uploaded payroll files and returns a decision based on the validation results
# process_uploaded_master(): processes uploaded master files and returns a decision based on the validation results
# GetFileName(): gets all uploaded master files from a specified folder
# Check_Auditing_Validation(): checks if there is a result from auditing or not
# Handel_Living_Housing_Social_Validation_File(): handles the validation of living, housing, and social allowance files.
# """

import glob
import os
import re
import pandas as pd
from flask_login import current_user
from flask import session
from application.home.file_processing import get_uploads_folder, generate_file_name, InitialValidatFile, Initial_Formating


def dataframe_allowing_duplicate_headers(dataframe):
    """
    this function will work as following
        any duplicate column names it will be renamed them as it is e.g. CPR_NO, CPR_NO.1, CPR_NO.2 keep them all as CPR_NO
    Parameters
    ----------
    dataframe: the uploaded data frame

    Returns
    -------
    updated data frame after returning duplicate column names as it is
    """
    # To Hold All The Possible Duplicate Tags ['.1', '.2', '.3', ...]
    dup_id_range = []

    # Generate And Store All The Possible Duplicate Tags ['.1', '.2', '.3', ...]
    for count in range(0, len(dataframe.columns)):
        dup_id_range.append('.{}'.format(count))

    # Search And Replace All Duplicate Headers To What It Was Set As Originally
    def rename(dataframe, character_number):
        duplicate_columns_chars = list(
            filter(lambda v: v[(len(v) - character_number):] in dup_id_range,
                   dataframe.columns))

        for duplicate_column in duplicate_columns_chars:
            dataframe = dataframe.rename(
                columns={duplicate_column: duplicate_column[:-character_number]})
        return dataframe

    # Replace The Possible Duplicates Respectfully Based On Columns Count
    if len(dup_id_range) > 0:
        dataframe = rename(dataframe, 2)
        if len(dup_id_range) > 9:
            dataframe = rename(dataframe, 3)
            if len(dup_id_range) > 99:
                dataframe = rename(dataframe, 4)
                # If You Have More Than A Thousand Columns (lol)
                # if len(dup_id_range) > 999:
                #    dataframe = rename(dataframe, 5)

    return dataframe


def initilizePayrollFormVariable():
    # you can also use sheet_index [0,1,2..] instead of sheet name.
    sheet_num = 0
    # append lists for all payroll files
    success_list = []
    success_sheet = []
    missing_list = []
    missing_sheet = []
    conflict_list1 = []
    conflict_sheet = []
    exists_list = []
    exists_sheet = []
    incorrect_list = []
    incorrect_sheet = []
    number_of_sheets = 0  # count how many sheets we have in uploaded file
    saved_preprocessed_df = {}
    sheet_to_df_map = {}
    optional_sheet = []
    optional_list = []
    return sheet_num, success_list, success_sheet, missing_list, missing_sheet, conflict_list1, \
           conflict_sheet, exists_list, exists_sheet, incorrect_list, incorrect_sheet, number_of_sheets, saved_preprocessed_df, sheet_to_df_map, optional_list, optional_sheet


## function to validate sheet name ##
def Validate_ShhetName(xls, file_type):
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEPT', 'OCT', 'NOV', 'DEC']
    sheetname = []  # list to store all invalid sheet name

    # check the validation of sheet names
    for sheet_name in xls.sheet_names:
        sheet_name = sheet_name.upper()
        sheet_name = sheet_name.replace(" ", "")
        split = sheet_name.split("-")
        if len(split) > 1:
            month, yearinsheet = split  # if payroll then yearinsheet will containes year if master then should contains MASTER
            if file_type == 'Payroll':
                match_year = re.match(r'.*([1-3][0-9]{3})', yearinsheet)
                if match_year is None:
                    sheetname.append(sheet_name)
                if month not in months:
                    sheetname.append(sheet_name)
            elif file_type == 'Master':
                if yearinsheet != 'MASTER':
                    sheetname.append(sheet_name)
                if month not in months:
                    sheetname.append(sheet_name)
        else:
            sheetname.append(sheet_name)

    return sheetname


######################################################################################-->
######################### Process uploaded master sheet ##############################-->
######################################################################################-->
def process_master_form(form):
    f = form.master.data
    file_name1 = f.filename.split('.')[0]
    # current_path = os.path.abspath(file_name)
    extension = os.path.splitext(f.filename)[1]
    session['extension' + str(current_user.username)] = extension
    path = get_uploads_folder("master_data")
    session['path' + str(current_user.username)] = path
    # this process
    filename = generate_file_name(str(file_name1), extension)
    session['file_name' + str(current_user.username)] = filename
    folderName = "master_data"

    xls = pd.ExcelFile(f)

    # validate sheetname
    sheetname = Validate_ShhetName(xls, 'Master')
    # sheet name will havelist of all invalid sheet name
    if sheetname:
        different = 'invalidsheet'
        # drop duplocate sheet name
        sheetname = list(dict.fromkeys(sheetname))
        return different, sheetname, [], pd.DataFrame()

    # to read all sheets to a map
    sheet_to_df_map = {}
    for sheet_name in xls.sheet_names:
        sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

    # you can also use sheet_index [0,1,2..] instead of sheet name.
    for key in sheet_to_df_map:
        new_file = sheet_to_df_map[key]
    # new_file = dataframe_allowing_duplicate_headers(new_file)  # any duplicate rename it as it is e.g. CPR_NO, CPR_NO.1, CPR_NO.2 keep them all as CPR_NO
    new_file = Initial_Formating(new_file)

    # new_file = read_file(f)
    # new_file = Initial_Formating(new_file)

    approved_columns = []  # this will be empty becuase in intitial validation file we still didnt know if there is an conflict columns or not
    different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,
                                                                                     approved_columns)

    if different == True:
        created_path = path + '/' + filename
        saved_preprocessed_df = {}
        saved_preprocessed_df[xls.sheet_names[0]] = new
        for key in saved_preprocessed_df:
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        success = 'success'
        return success, [], [], pd.DataFrame()
    elif different == 'exists':
        exists = 'exists'
        return exists, [], [], pd.DataFrame()
    elif different == 'Conflict':
        temp_folder_path = path + '/MasterTemprory'
        # i folder not exisit created
        if not os.path.exists(temp_folder_path):
            os.makedirs(temp_folder_path)
        global temp_filePath
        temp_filePath = temp_folder_path + '/' + file_name1 + '.xlsx'
        writer = pd.ExcelWriter(temp_filePath, engine="xlsxwriter")
        for sheet_name in xls.sheet_names:
            result_df = pd.DataFrame(xls.parse(sheet_name))
            # print(result_df)
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
        # store the file in temroray file
        # new.to_excel(temp_filePath)

        # set the key dicesion to show the pop up to the end user
        session['temp_path' + str(current_user.username)] = temp_filePath
        return different, conflict_list, [], pd.DataFrame()
    elif different == 'MissingColumns':
        # temp_filePath.remove()
        # xls.close()
        # os.remove(temp_filePath)
        return different, [], coulmns_not_in_uploaded_file, ''  # incorrect columns names to notify end users
    else:
        incorrect = 'incorrect'
        return incorrect, [], [], pd.DataFrame()


######################################################################################-->
##################### Process uploaded overtime payroll sheet #######################-->
######################################################################################-->
def processPayrollForm(form):
    sheet_num, success_list, success_sheet, missing_list, missing_sheet, conflict_list1, \
    conflict_sheet, exists_list, exists_sheet, incorrect_list, incorrect_sheet, number_of_sheets, saved_preprocessed_df, sheet_to_df_map, optional_list, optional_sheet = initilizePayrollFormVariable()
    # the approved file
    f = form.PayRoll.data
    file_name1 = f.filename.split('.')[0]
    # current_path = os.path.abspath(file_name)
    extension = os.path.splitext(f.filename)[1]
    path = get_uploads_folder("MonthlyPayroll_data")
    session['path' + str(current_user.username)] = path
    # this process
    filename = generate_file_name(str(file_name1), extension)
    session['file_name' + str(current_user.username)] = filename
    folderName = "MonthlyPayroll_data"

    xls = pd.ExcelFile(f)

    # validate sheetname
    sheetname = Validate_ShhetName(xls, 'Payroll')
    # sheet name will havelist of all invalid sheet name
    if sheetname:
        different = 'invalidsheet'
        # drop duplocate sheet name
        sheetname = list(dict.fromkeys(sheetname))
        return different, sheetname, [], pd.DataFrame(), '', [], [], optional_list, optional_sheet

    # to read all sheets to a map
    for sheet_name in xls.sheet_names:
        sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

    # you can also use sheet_index [0,1,2..] instead of sheet name.
    for key in sheet_to_df_map:
        number_of_sheets = number_of_sheets + 1
        new_file = sheet_to_df_map[key]
        new_file = dataframe_allowing_duplicate_headers(
            new_file)  # any duplicate rename it as it is e.g. CPR_NO, CPR_NO.1, CPR_NO.2 keep them all as CPR_NO
        new_file = Initial_Formating(new_file)
        # print(new_file.columns)

        approved_columns = []  # this will be empty becuase in intitial validation file we still didnt know if there is an conflict columns or not
        different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,
                                                                                         approved_columns)

        # check if optional columns in list
        if ('HOLIDAY_OT_HOURS' in coulmns_not_in_uploaded_file) or ('REGULAR_OT_HOURS' in coulmns_not_in_uploaded_file):
            optional_list.append(coulmns_not_in_uploaded_file)
            optional_sheet.append(xls.sheet_names[sheet_num])

        # print(different)
        if different == True:
            success_list.append('success')
            success_sheet.append(xls.sheet_names[sheet_num])
            saved_preprocessed_df[xls.sheet_names[sheet_num]] = new
            sheet_num = sheet_num + 1
        elif different == 'MissingColumns':
            missing_list.append(coulmns_not_in_uploaded_file)
            missing_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1
        elif different == 'Conflict':
            conflict_list1.append(conflict_list)
            conflict_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1
        elif different == 'exists':
            exists_list.append('exists')
            exists_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1
        else:
            incorrect_list.append('incorrect')
            incorrect_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1

    if conflict_list1 or optional_list:
        # remove duplicate conflict if it exsist will apply for all sheets
        #### if there is a conflict columns means i need to save the uploaded file temporary###
        # create a path
        temp_folder_path = path + '/PayrollTemprory'

        # i folder not exisit created
        if not os.path.exists(temp_folder_path):
            os.makedirs(temp_folder_path)
        global temp_filePath
        temp_filePath = temp_folder_path + '/' + file_name1 + '.xlsx'
        # initialize excel file
        writer = pd.ExcelWriter(temp_filePath, engine="xlsxwriter")
        # set the key dicesion to show the pop up to the end user
        different = 'PayrollConflict'
        session['temp_path' + str(current_user.username)] = temp_filePath

        for sheet_name in xls.sheet_names:
            result_df = pd.DataFrame(xls.parse(sheet_name))
            # print(result_df)
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
        return different, conflict_list1, conflict_sheet, pd.DataFrame(), '', [], [], optional_list, optional_sheet
    elif exists_list and success_list and missing_list:
        different = 'success'
        different1 = 'exists'
        different2 = 'MissingColumnsPayroll'

        for key in saved_preprocessed_df:
            created_path = path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        # return different, exists_sheet, different1,different2, success_sheet,missing_list,missing_sheet
        return different, exists_sheet, different1, different2, success_sheet, missing_list, missing_sheet, optional_list, optional_sheet
    elif exists_list and success_list:
        different = 'success'
        different1 = 'exists'
        for key in saved_preprocessed_df:
            created_path = path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        return different, exists_sheet, different1, pd.DataFrame(), success_sheet, [], [], optional_list, optional_sheet
    elif missing_list and success_list:
        different = 'success'
        different1 = 'MissingColumnsPayroll'
        for key in saved_preprocessed_df:
            created_path = path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        return different, missing_sheet, different1, missing_list, success_sheet, [], [], optional_list, optional_sheet
    elif missing_list and exists_list:
        different = 'exists'
        different1 = 'MissingColumnsPayroll'
        return different, missing_sheet, different1, missing_list, exists_sheet, [], [], optional_list, optional_sheet
    elif missing_list:
        different = 'MissingColumnsPayroll'
        return different, missing_sheet, missing_list, pd.DataFrame(), '', [], [], optional_list, optional_sheet  # incorrect columns names to notify end users
    elif exists_list:
        different = 'exists'
        # print(exists_sheet)
        return different, exists_sheet, [], pd.DataFrame(), '', [], [], optional_list, optional_sheet
    elif len(success_list) == number_of_sheets:
        different = 'success'
        for key in saved_preprocessed_df:
            created_path = path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        return different, [], [], pd.DataFrame(), '', [], [], optional_list, optional_sheet
        # print(created_path)
        # print(saved_preprocessed_df[key])
    elif incorrect_list:
        different = 'incorrect'
        return different, [], [], pd.DataFrame(), '', [], [], optional_list, optional_sheet


"""
<-- ### Complete the Process of uploaded Payroll sheet when confirm conflict columns#####-->
"""


def process_uploaded_payroll(reciebed_optional_columns, received_optional_sheets, approved_columns, folderName):
    sheet_num, success_list, success_sheet, missing_list, missing_sheet, conflict_list1, \
    conflict_sheet, exists_list, exists_sheet, incorrect_list, incorrect_sheet, number_of_sheets, saved_preprocessed_df, sheet_to_df_map, optional_list, optional_sheet = initilizePayrollFormVariable()
    # this path the temprory path
    tem_path = session['temp_path' + str(current_user.username)] if 'temp_path' + str(
        current_user.username) in session else ""
    # this path the path will save cleaned file inside it
    final_path = session['path' + str(current_user.username)] if 'path' + str(current_user.username) in session else ""
    filename = session['file_name' + str(current_user.username)] if 'file_name' + str(
        current_user.username) in session else ""

    # to read all sheets to a map
    xls = pd.ExcelFile(tem_path)

    for sheet_name in xls.sheet_names:
        sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

    count_opt_sheet = 0
    # for key in sheet_to_df_map:
    for key in sheet_to_df_map:
        number_of_sheets = number_of_sheets + 1
        new_file = sheet_to_df_map[key]
        new_file = dataframe_allowing_duplicate_headers(new_file)  # any duplicate rename it as it is e.g. CPR_NO, CPR_NO.1, CPR_NO.2 keep them all as CPR_NO
        if received_optional_sheets:
            # if key in received_optional_sheets:
            if key == received_optional_sheets[count_opt_sheet]:
                ## this section need to work on ###
                if 'HOLIDAY_OT_HOURS' in reciebed_optional_columns[count_opt_sheet]:
                    new_file['HOLIDAY_OT_HOURS'] = 0
                if 'REGULAR_OT_HOURS' in reciebed_optional_columns[count_opt_sheet]:
                    new_file['REGULAR_OT_HOURS'] = 0
                if  count_opt_sheet < len(received_optional_sheets)-1:
                    count_opt_sheet = count_opt_sheet + 1

        new_file = Initial_Formating(new_file)

        different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,
                                                                                         approved_columns)

        if different == True:
            success_list.append('success')
            success_sheet.append(xls.sheet_names[sheet_num])
            # save success files in dictionary with its sheet name as a key
            saved_preprocessed_df[xls.sheet_names[sheet_num]] = new
            sheet_num = sheet_num + 1

        elif different == 'MissingColumns':
            missing_list.append(coulmns_not_in_uploaded_file)
            missing_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1

            # # check if optional columns in list
            # print(missing_list)
            # if 'HOLIDAY_OT_HOURS' not in missing_list:
            #     print('yes (HOLIDAY_OT_HOURS) column not in df')
            # if 'REGULAR_OT_HOURS' not in missing_list:
            #     print('yes (REGULAR_OT_HOURS) column not in df')
        elif different == 'Conflict':
            conflict_list1.append(conflict_list)
            conflict_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1
        elif different == 'exists':
            exists_list.append('exists')
            exists_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1
        else:
            incorrect_list.append('incorrect')
            incorrect_sheet.append(xls.sheet_names[sheet_num])
            sheet_num = sheet_num + 1

    # Take decsision based on the above process
    if conflict_list1:
        # remove duplicate conflict if it exsist will apply for all sheets
        #### if there is a conflict columns means i need to save the uploaded file temporary###
        # create a path
        temp_folder_path = final_path + '/PayrollTemprory'

        # i folder not exisit created
        if not os.path.exists(temp_folder_path):
            os.makedirs(temp_folder_path)
        temp_filePath = temp_folder_path + '/' + filename + '.xlsx'
        # initialize excel file
        writer = pd.ExcelWriter(temp_filePath, engine="xlsxwriter")
        # set the key dicesion to show the pop up to the end user
        different = 'PayrollConflict'
        session['temp_path' + str(current_user.username)] = temp_filePath
        for sheet_name in xls.sheet_names:
            result_df = pd.DataFrame(xls.parse(sheet_name))
            # print(result_df)
            result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
        return different, conflict_list1, conflict_sheet, [], [], [], []


    elif exists_list and success_list and missing_list:
        different = 'success'
        different1 = 'exists'
        different2 = 'MissingColumnsPayroll'
        for key in saved_preprocessed_df:
            created_path = final_path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        xls.close()
        os.remove(tem_path)
        return different, exists_sheet, different1, success_sheet, different2, missing_list, missing_sheet
    elif exists_list and success_list:
        different = 'success'
        different1 = 'exists'
        for key in saved_preprocessed_df:
            created_path = final_path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        xls.close()
        os.remove(tem_path)
        return different, exists_sheet, different1, success_sheet, [], [], []
    elif missing_list and success_list:
        different = 'success'
        different1 = 'MissingColumnsPayroll'
        for key in saved_preprocessed_df:
            created_path = final_path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        xls.close()
        os.remove(tem_path)
        return different, missing_sheet, different1, success_sheet, missing_list, [], []
    elif missing_list and exists_list:
        different = 'exists'
        different1 = 'MissingColumnsPayroll'
        xls.close()
        os.remove(tem_path)
        return different, missing_sheet, different1, exists_sheet, missing_list, [], []
    elif missing_list:
        different = 'MissingColumnsPayroll'
        xls.close()
        os.remove(tem_path)
        return different, missing_sheet, missing_list, [], [], [], []  # incorrect columns names to notify end users

    elif exists_list:
        different = 'exists'
        xls.close()
        os.remove(tem_path)
        return different, exists_sheet, [], [], [], [], []
    elif len(success_list) == number_of_sheets:
        different = 'success'
        for key in saved_preprocessed_df:
            created_path = final_path + '/' + key + '-' + filename
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)
        # os.close(tem_path)
        xls.close()
        os.remove(tem_path)
        return different, [], [], [], [], [], []

    elif incorrect_list:
        different = 'incorrect'
        return different, [], [], [], [], [], []


## this section need to work on ##
# once there is a missing columns need to make sure these missing column did not contains HOLIDAY_OT_HOURS REGULAR_OT_HOURS
#     elif missing_list:
#         i = 0
#         not_manditory_columns = {}
#         # loop through sheet by sheet
#         for sheet in missing_sheet:
#             # this will be applied for the first time only to create a list for each key
#             if not_manditory_columns.get(sheet) == None:
#                 not_manditory_columns[sheet] = []
#             # if the following column are missing add them in a dictionary of list
#             if 'HOLIDAY_OT_HOURS' in missing_list[i]:
#                 not_manditory_columns[sheet].append("HOLIDAY_OT_HOURS")
#             if 'REGULAR_OT_HOURS' in missing_list[i]:
#                 not_manditory_columns[sheet].append("REGULAR_OT_HOURS")
#             i = i +1
#         # if there is a missing columns with  HOLIDAY_OT_HOURS REGULAR_OT_HOURS then will save last version of uploaded file and get confirmation from end user to add them
#         if not_manditory_columns:
#             # set the key dicesion to show the pop up to the end user
#             different = 'not_mandit_col'
#             return different, missing_sheet, '', exists_sheet, missing_list, not_manditory_columns, []

"""
<-- ### Complete the Process of uploaded master sheet when confirm conflict columns#####-->
"""


def process_uploaded_master(approved_columns, folderName):
    # Remove space from columns names

    # filename = session['file_name'+ str(current_user.username)] if 'file_name'+ str(current_user.username) in session else ""
    # path = session['path'+ str(current_user.username)] if 'path'+ str(current_user.username) in session else ""
    #
    # this path the temprory path
    tem_path = session['temp_path' + str(current_user.username)] if 'temp_path' + str(
        current_user.username) in session else ""
    # this path the path will save cleaned file inside it
    final_path = session['path' + str(current_user.username)] if 'path' + str(current_user.username) in session else ""
    filename = session['file_name' + str(current_user.username)] if 'file_name' + str(
        current_user.username) in session else ""

    # to read all sheets to a map
    xls = pd.ExcelFile(tem_path)
    sheet_to_df_map = {}
    for sheet_name in xls.sheet_names:
        sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

    for key in sheet_to_df_map:
        new_file = sheet_to_df_map[key]

    # new_file = dataframe_allowing_duplicate_headers(new_file)  # any duplicate rename it as it is e.g. CPR_NO, CPR_NO.1, CPR_NO.2 keep them all as CPR_NO

    # new_file = pd.read_excel(tem_path)
    new_file = Initial_Formating(new_file)

    different, conflict_list, coulmns_not_in_uploaded_file, new = InitialValidatFile(new_file, folderName,
                                                                                     approved_columns)

    if different == True:
        # you can do the cleaning df here
        created_path = final_path + '/' + filename
        # new.to_excel(created_path, index=False)
        success = 'success'
        saved_preprocessed_df = {}
        print(xls.sheet_names[0])
        saved_preprocessed_df[xls.sheet_names[0]] = new
        for key in saved_preprocessed_df:
            saved_preprocessed_df[key].to_excel(created_path, index=False, sheet_name=key)

            # os.close(tem_path)
        xls.close()
        os.remove(tem_path)
        # print(created_path)
        return success, []
    elif different == 'exists':
        exists = 'exists'
        xls.close()
        os.remove(tem_path)
        # os.remove(tem_path)
        return exists, []
    elif different == 'MissingColumns':
        xls.close()
        os.remove(tem_path)
        # os.remove(tem_path)
        return different, coulmns_not_in_uploaded_file  # incorrect columns names to notify end users
    else:
        xls.close()
        os.remove(tem_path)
        incorrect = 'incorrect'
        return incorrect, []


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
        full_path = str(path) + '/' + str(file)
        full_paths.append(full_path)

    return full_paths, files


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
