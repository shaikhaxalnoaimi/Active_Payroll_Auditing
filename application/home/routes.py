"""
File Name: application\home\routes.py

Purpose: This file contains the main code for the web application. It handles the routing, rendering of templates, and processing of data.

Dependencies:

Flask (version 2.0.1)
pandas (version 1.3.1)
openpyxl (version 3.0.7)
flask_wtf (version 0.15.1)
wtforms (version 2.3.3)
flask_login (version 0.5.0)
flask_sqlalchemy (version 2.5.1)
flask_migrate (version 3.1.0)
flask_bootstrap (version 4.6.0)
flask_uploads (version 0.2.1)
flask_cors (version 3.0.10)
flask_wtf.csrf (version 0.15.1)
Code Structure:

Import necessary modules and packages
Initialize Flask app and set configurations
Initialize database and migration
Define User model for authentication
Define routes for login, logout, and registration
Define routes for uploading and processing master and payroll files
Define routes for managing uploaded files
Define routes for downloading auditing reports
Define helper function for getting current page name from request
Define error handlers for 403 and CSRF errors
Run the app if executed directly
"""


import os

import pandas as pd
from jinja2 import TemplateNotFound

# from application import connection_check, get_internet_date
from application import generate_report_path
from application.home import blueprint
from flask_login import login_required, current_user

from flask import render_template, request, send_file, session

from application.home.allowance_data_preprocessing import Check_Living_Allowance, Check_Social_Allowance, \
    Check_Housing_Allowance, noGradeWithAllowance, noMaterialStatuseWithAllowance, Check_Special_Allowance, \
    Check_Car_Allowance, \
    Check_Communication_Allowance, Prepare_Employee_Allowance_report, Check_Car_and_Transport, checkTransportAllowance
from application.home.data_processing import Check_Duplicate_Name, Check_Invalid_CPR, Check_Missing_Name, \
    Check_Duplicate_CPR, Check_Duplicate_Accont_No, Check_Invalid_Account_No, Check_Age, Check_Annual_leave, \
    Check_Sick_leave, Check_High_Rank_Posisiton, Prepare_Employee_Information_report, \
    Check_Pension_Allowance, Check_Social_Allowance_Deduction, Check_Unemployment_Allowance_Deduction, \
    Import_Master_Data, Import_Payroll_Data, Prepare_Employee_Deduction_report, Missing_GRADE, \
    Missing_MARITAL_STATUS, Check_Categories, Missing_Employee
from application.home.forms import MasterSheetForm, PayRollSheetForm, SelectMasterForm, selectPayrollForm
from application.home.overtime_data_preprocessing import check_overtime, Prepare_Employee_Overtime_report, \
    notAllowedOvertime

from application.home.util import process_master_form, \
    Check_Auditing_Validation, GetFileName, processPayrollForm, process_uploaded_master, process_uploaded_payroll

from path_system import secure_join
from flask_wtf.csrf import CSRFProtect,CSRFError

csrf = CSRFProtect()

# get the directory of generated folder
file_path = generate_report_path()
dic_list2 = {}

# BASE_DIR = base_dir()
def selectFormInitilization():
    global dic_list2
    selectform_master = SelectMasterForm()
    selectform_payroll = selectPayrollForm()

    """
      ___________initial fill drop down list_____________
    """
    # Master
    # pass folder name
    full_paths_master, files_master = GetFileName("master_data")
    selectform_master.directories.choices = [("", "--- Select Employee Master ---")] + [(file_master, file_master)
                                                                                        for
                                                                                        file_master, file_master in
                                                                                        zip(files_master,
                                                                                            files_master)]

    dic_list2 = {files_master: 'master_data' for files_master in files_master}

    # Payroll
    full_paths_payroll, files_payroll = GetFileName("MonthlyPayroll_data")
    selectform_payroll.directories_payroll.choices = [("", "  --- Select Employee Payroll ---")] + [
        (file_payroll, file_payroll) for
        file_payroll, file_payroll in
        zip(files_payroll, files_payroll)]



    dic_list2.update({k: "MonthlyPayroll_data" for k in files_payroll})
    return selectform_master, selectform_payroll, full_paths_payroll, files_payroll


def objectFormInitilization():
    # create object from requited forms
    master_upload_form = MasterSheetForm()
    payroll_upload_form = PayRollSheetForm()

    return master_upload_form, payroll_upload_form


def variableInitilization():
    """
    This function to initialize all the variable in this file.
    Returns
    -------
    RecivedMessage: str
        initiate string values to receive the status of message that will be raise to the end user  (exists, success, conflict Columns, Missing Columns)
    file_path: str
        initiate string values to set up the full path of the uploaded file
    conflict_list: list
        initiate list to set up the conflict columns names if any (e.g. [['SOCIAL','SOCIAL_PFC'], ['GRADE', 'APPROVED_GRADE'])
    missing_columns: list
       initiate list to set up the  missing columns names of the uploaded file (if any) (e.g. ['EMPLOYEE_NAME', ['EMPLOYEE_CPR'])
    received_value: dataframe
        initiate dataframe to restore the uploaded file (only if need to confirm the conflict column names)
    error: boolean
        initiate boolean values for checking and validation purposes
    auditing_button: boolean

    """
    # initiate string values for checking and validation purposes
    value = ''

    RecivedMessage = ''
    key = ''
    file_path = ''
    missing_list = []
    conflict_list = []
    conflict_sheet = []  ## sheets names that contains conflict column name
    missing_columns = []
    sucess_sheet = []
    recevied_list = []
    val2 = []
    val3 = []
    approved_columns = []
    optional_column = []
    optional_sheet = []
    # this data only if need to confirm the conflict column names
    received_value = pd.DataFrame()
    # initiate boolean values for checking and validation purposes
    error = False
    # initiate boolean values true if end user try to click on auditing button without select file name
    auditing_button = False
    # initiate Dataframes to store imported data to apply auditing process on it
    global df
    df = pd.DataFrame()

    return RecivedMessage, file_path, conflict_list, missing_columns, received_value, error, auditing_button, df, key, value, conflict_sheet, missing_list, \
           sucess_sheet, recevied_list, val2, val3, approved_columns, optional_column, optional_sheet


"""
<--#####################Master Conflict Model ###########################-->
"""


@blueprint.route('/conflict', methods=["POST", "GET"])
@login_required
def conflict():
    # variable Initilization
    RecivedMessage, file_path, conflict_list, missing_columns, received_value, error, auditing_button, df, key, value, conflict_sheet, missing_list, \
    sucess_sheet, recevied_list, val2, val3, approved_columns, optional_column, optional_sheet = variableInitilization()
    # create object from requited forms
    master_upload_form, payroll_upload_form = objectFormInitilization()
    selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()

    if request.form['action'] == 'Confirm':
        # get list of list to use unique name of radion button
        conflicts = request.form.getlist("coflict_list")

        # approved_columns = []
        for conflict in conflicts:
            # print(conflicts)
            # print('___')
            # print(request.form.get(conflict))
            confirmed_column = request.form.get(conflict)  # conflict (radio button name)
            approved_columns.append(confirmed_column)

        folder_name = session['folder_name' + str(current_user.username)] if 'folder_name' + str(
            current_user.username) in session else ""
        # folder_name = "master_data"

        # CHECK IF THE UPLOADED FILE MASTER OR PAYROLL BEFOR UPLODED TO THE SYSTEM
        try:
            # print(df.columns)
            RecivedMessage, missing_columns = process_uploaded_master(approved_columns, folder_name)
            # create object from requited forms

            selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()
        except Exception as ex:
            value = str(ex)
            error = True

    return render_template('home/index.html', segment="index",
                           # exception error of fail file upload
                           error=error,
                           # recieved upload message (exists, success, conflict Columns, Missing Columns)
                           RecivedMessage=RecivedMessage,
                           # if there is a missing columns send them to enduser
                           missing_columns=missing_columns,
                           missing_list=missing_list,
                           # master upload form
                           master_upload_form=master_upload_form,
                           # payroll upload form
                           payroll_upload_form=payroll_upload_form,
                           # dropdown master file name
                           selectform_master=selectform_master,
                           # dropdown payroll file
                           selectform_payroll=selectform_payroll,
                           full_paths_payroll=full_paths_payroll,
                           files_payroll=files_payroll,
                           value=value,
                           zip=zip)


"""
<--#####################Payroll Conflict Model ###########################-->
"""


@blueprint.route('/conflict2', methods=["POST", "GET"])
@login_required
def conflict2():
    # variable Initilization
    RecivedMessage, file_path, conflict_list, missing_columns, received_value, error, auditing_button, df, key, value, conflict_sheet, missing_list, \
    sucess_sheet, recevied_list, val2, val3, approved_columns, optional_column, optional_sheet = variableInitilization()
    # create object from requited forms
    master_upload_form, payroll_upload_form = objectFormInitilization()
    selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()

    if request.form['action'] == 'Confirm':
        # get list of list to use unique name of radion button
        conflicts = request.form.getlist("conflicts")
        # approved_columns = []
        for conflict in conflicts:
            confirmed_column = request.form.get(conflict)  # conflict (radio button name)
            approved_columns.append(confirmed_column)

        folder_name = session['folder_name' + str(current_user.username)] if 'folder_name' + str(
            current_user.username) in session else ""
        optional_column = session['optional_column' + str(current_user.username)] if 'optional_column' + str(
            current_user.username) in session else ""
        optional_sheet = session['optional_sheet' + str(current_user.username)] if 'optional_sheet' + str(
            current_user.username) in session else ""
        session['approved_columns_session' + str(current_user.username)] = approved_columns

        # CHECK IF THE UPLOADED FILE MASTER OR PAYROLL BEFOR UPLODED TO THE SYSTEM
        # try:
        # missing columns here is a list of sheet name if there is a missing columns
        RecivedMessage, missing_columns, missing_list, sucess_sheet, recevied_list, val2, val3 = process_uploaded_payroll(
            optional_column, optional_sheet, approved_columns, folder_name)
        session['approved_not_mandatory_columns' + str(current_user.username)] = val2
        # create object from requited forms
        selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()
        # except Exception as ex:
        #     value = str(ex)
        #     error = True

    # print(missing_columns)
    # print(missing_list)
    return render_template('home/index.html', segment="index",
                           # exception error of fail file upload
                           error=error,
                           # recieved upload message (exists, success, conflict Columns, Missing Columns)
                           RecivedMessage=RecivedMessage,
                           # if there is a missing columns send list of sheet names that have missing column names
                           missing_columns=missing_columns,
                           # if there is a missing column names return list of columns
                           missing_list=missing_list,
                           # master upload form
                           master_upload_form=master_upload_form,
                           # payroll upload form
                           payroll_upload_form=payroll_upload_form,
                           # dropdown master file name
                           selectform_master=selectform_master,
                           # dropdown payroll file
                           selectform_payroll=selectform_payroll,
                           full_paths_payroll=full_paths_payroll,
                           files_payroll=files_payroll,
                           value=value,
                           sucess_sheet=sucess_sheet,
                           recevied_list=recevied_list,
                           val2=val2,
                           val3=val3,
                           zip=zip)



from flask import session

"""
<--###########index page (Employee Information Audit)#############-->
"""
# @app.limiter.limit("1/minute")
@blueprint.route('/index', methods=["POST", "GET"])
@login_required
def index():
    if not session.get('logged_in'):
        return render_template('auth/login.html',
                               segment='login',
                               msg='You have exceeded the maximum number of login attempts. Please try again later.',
                               # form=login_form
                               )
    # variable Initilization
    RecivedMessage, file_path, conflict_list, missing_columns, received_value, error, auditing_button, df, key, value, conflict_sheet, missing_list, \
    sucess_sheet, recevied_list, val2, val3, approved_columns, optional_column, optional_sheet = variableInitilization()

    # create object from requited forms
    master_upload_form, payroll_upload_form = objectFormInitilization()
    # fill the dropdown list with uploaded files (path)
    selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()

    """
    ___________upload file and update drop down list_____________
    """
    if request.method == 'POST':
        if 'master' in request.files and master_upload_form.validate_on_submit():
            session['folder_name' + str(current_user.username)] = 'master_data'
            # CHECK IF THE UPLOADED FILE MASTER OR PAYROLL BEFOR UPLODED TO THE SYSTEM
            try:
                RecivedMessage, conflict_list, missing_columns, received_value = process_master_form(
                    master_upload_form)
            except Exception as ex:
                value = str(ex)
                error = True

            # update the drop downlist with new added files
            selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()
        elif 'PayRoll' in request.files and payroll_upload_form.validate_on_submit():
            session['folder_name' + str(current_user.username)] = 'MonthlyPayroll_data'
            try:
                RecivedMessage, conflict_list, missing_columns, received_value, sucess_sheet, val2, val3, optional_column, optional_sheet = processPayrollForm(
                    payroll_upload_form)

                if RecivedMessage == 'PayrollConflict':
                    ## if there is any conflict in the uploaded file missing columns it will be sheet names  for employee payroll i will use them in conflict2 function
                    session['optional_sheet' + str(current_user.username)] = optional_sheet
                    session['optional_column' + str(current_user.username)] = optional_column
                    session['sheet_name' + str(current_user.username)] = missing_columns
            except Exception as ex:
                value = str(ex)
                error = True

            selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()
    return render_template('home/index.html', segment="index",
                           # exception error of fail file upload
                           error=error,
                           # master upload form
                           master_upload_form=master_upload_form,
                           # payroll upload form
                           payroll_upload_form=payroll_upload_form,
                           # recieved upload message (exists, success, conflict Columns, Missing Columns)
                           RecivedMessage=RecivedMessage,
                           missing_list=missing_list,
                           # if there is a conflict columns show them to the enduser
                           conflict_list=conflict_list,
                           # key shows the sheet name to know in witch sheet we have missing name
                           key=key,
                           # if there is a missing columns send them to enduser
                           missing_columns=missing_columns,
                           # if there is an optional column return list of them and list of sheet name
                           optional_column=optional_column,
                           optional_sheet=optional_sheet,
                           # dropdown master file name
                           selectform_master=selectform_master,
                           selectform_payroll=selectform_payroll,
                           # return path to check if there is a path
                           file_path=file_path,
                           # inform if auditing button clicked or no
                           auditing_button=auditing_button,
                           # multiple dropdown list for payroll
                           full_paths_payroll=full_paths_payroll,
                           # the sheet names that have conflict column
                           conflict_sheet=conflict_sheet,
                           files_payroll=files_payroll,
                           value=value,
                           sucess_sheet=sucess_sheet,
                           received_value=received_value,
                           val2=val2,
                           val3=val3,
                           zip=zip)



def auditingVariablesInitlization():
    file_path = True
    no_duplicate_name = True
    no_missing_name = True
    no_duplicate_cpr = True
    no_invalid_CPR = True
    no_duplicate_acount_no = True
    no_invalid_account_no = True
    no_invalid_age = True
    no_invalid_annual = True
    no_invalid_sick_leave = True
    no_duplicate_high_rank_posisiton = True
    no_missing_material_status = True
    no_missing_grade = True
    no_missing_category = True
    no_employee_not_in_master = True
    no_employee_not_in_payroll = True
    error = ''

    duplicate_name = pd.DataFrame()
    missing_name = pd.DataFrame()
    invalid_CPR = pd.DataFrame()
    duplicate_cpr = pd.DataFrame()
    duplicate_acount_no = pd.DataFrame()
    invalid_account_no = pd.DataFrame()
    invalid_age = pd.DataFrame()
    invalid_annual = pd.DataFrame()
    invalid_sick_leave = pd.DataFrame()
    duplicate_high_rank_posisiton = pd.DataFrame()
    missing_grade = pd.DataFrame()
    missing_material_status = pd.DataFrame()
    missing_category = pd.DataFrame()
    employee_not_in_master = pd.DataFrame()
    employee_not_in_payroll = pd.DataFrame()
    employee_info_counter = 0

    return file_path, no_duplicate_name, no_missing_name, no_duplicate_cpr, no_invalid_CPR, no_duplicate_acount_no, \
           no_invalid_account_no, no_invalid_age, no_invalid_annual, no_invalid_sick_leave, no_duplicate_high_rank_posisiton, no_missing_material_status, no_missing_grade, \
           no_employee_not_in_master, no_employee_not_in_payroll, error, duplicate_name, missing_name, invalid_CPR, duplicate_cpr, duplicate_acount_no, invalid_account_no, invalid_age, \
           invalid_annual, invalid_sick_leave, duplicate_high_rank_posisiton, missing_grade, missing_material_status, no_missing_category, missing_category, \
           employee_info_counter, employee_not_in_master, employee_not_in_payroll


def variableDeductionInitialization():
    sheetnames = {}
    no_invalid_pension_allowance = {}
    no_invalid_social_allowance_deduction = {}
    no_invalid_unemployment_allowance_deduction = {}

    invalid_pension_allowance = {}
    invalid_social_allowance_deduction = {}
    invalid_unemployment_allowance_deduction = {}

    return sheetnames, no_invalid_pension_allowance, no_invalid_social_allowance_deduction, no_invalid_unemployment_allowance_deduction, \
           invalid_pension_allowance, invalid_social_allowance_deduction, invalid_unemployment_allowance_deduction


def VariableAllowanceInitialization():
    check_car_allowance = {}
    invalid_living_allowance = {}
    invalid_social_allowance = {}
    invalid_housing_allowance = {}
    invalid_transport_allowance = {}
    allowance_with_nograde = {}
    invalid_special_allowance = {}
    no_car_transport_allowance = {}
    no_living_allowance = {}
    no_invalid_social_allowance = {}
    no_invalid_housing_allowance = {}
    no_invalid_transport_allowance = {}
    no_allowance_with_nograde = {}
    no_invalid_special_allowance = {}

    invalid_car_allow_position = {}
    invalid_car_allow_grade = {}
    normal_employee_60 = {}
    normal_employee_not60 = {}
    no_invalid_car_allow_position = {}
    no_invalid_car_allow_grade = {}
    no_normal_employee_60 = {}
    no_normal_employee_not60 = {}

    emp_high_positions_comm_allow = {}
    emp_not_high_positions_comm_allow = {}
    emp_not_high_positions_invalid_comm_allow = {}

    no_emp_high_positions_comm_allow = {}
    no_emp_not_high_positions_comm_allow = {}
    no_emp_not_high_positions_invalid_comm_allow = {}
    allowance_with_nomaterial = {}
    no_allowance_with_nomaterial = {}

    return check_car_allowance, no_car_transport_allowance, invalid_living_allowance, invalid_transport_allowance, no_living_allowance, invalid_social_allowance, \
           no_invalid_social_allowance, invalid_housing_allowance, no_invalid_housing_allowance, no_invalid_transport_allowance, allowance_with_nograde, \
           no_allowance_with_nograde, invalid_special_allowance, no_invalid_special_allowance, invalid_car_allow_position, invalid_car_allow_grade, normal_employee_60, \
           normal_employee_not60, no_invalid_car_allow_position, no_invalid_car_allow_grade, no_normal_employee_60, no_normal_employee_not60, emp_high_positions_comm_allow, \
           emp_not_high_positions_comm_allow, emp_not_high_positions_invalid_comm_allow, no_emp_high_positions_comm_allow, no_emp_not_high_positions_comm_allow, \
           no_emp_not_high_positions_invalid_comm_allow, allowance_with_nomaterial, no_allowance_with_nomaterial


def VariableOvertimeInitialization():
    final_summary_regualr_overtime = pd.DataFrame()
    final_summary_holiday_overtime = pd.DataFrame()
    not_allowed_overtime = pd.DataFrame()
    no_final_summary_regualr_overtime = True
    no_final_summary_holiday_overtime = True
    no_not_allowed_overtime = True

    return final_summary_regualr_overtime, final_summary_holiday_overtime, not_allowed_overtime, no_final_summary_regualr_overtime, no_final_summary_holiday_overtime, no_not_allowed_overtime


@blueprint.route('/auditingProcess', methods=["POST", "GET"])
@login_required
def auditingProcess():
    value = ''
    error1 = False
    global master_df, payroll_file_path, msheetname,payroll_df
    master_df = pd.DataFrame()
    payroll_file_path = []
    # initialize variables of the employee information auditing process
    file_path, no_duplicate_name, no_missing_name, no_duplicate_cpr, no_invalid_CPR, no_duplicate_acount_no, \
    no_invalid_account_no, no_invalid_age, no_invalid_annual, no_invalid_sick_leave, no_duplicate_high_rank_posisiton, no_missing_material_status, no_missing_grade, \
    no_employee_not_in_master, no_employee_not_in_payroll, error, duplicate_name, missing_name, invalid_CPR, duplicate_cpr, duplicate_acount_no, invalid_account_no, invalid_age, \
    invalid_annual, invalid_sick_leave, duplicate_high_rank_posisiton, missing_grade, missing_material_status, no_missing_category, missing_category, \
    employee_info_counter, employee_not_in_master, employee_not_in_payroll = auditingVariablesInitlization()

    # initialize variable of the employee deduction auditing process
    sheetnames, no_invalid_pension_allowance, no_invalid_social_allowance_deduction, no_invalid_unemployment_allowance_deduction, \
    invalid_pension_allowance, invalid_social_allowance_deduction, invalid_unemployment_allowance_deduction = variableDeductionInitialization()

    # initialize variable for allowance auditing
    check_car_allowance, no_car_transport_allowance, invalid_living_allowance, invalid_transport_allowance, no_living_allowance, invalid_social_allowance, \
    no_invalid_social_allowance, invalid_housing_allowance, no_invalid_housing_allowance, no_invalid_transport_allowance, allowance_with_nograde, \
    no_allowance_with_nograde, invalid_special_allowance, no_invalid_special_allowance, invalid_car_allow_position, invalid_car_allow_grade, normal_employee_60, \
    normal_employee_not60, no_invalid_car_allow_position, no_invalid_car_allow_grade, no_normal_employee_60, no_normal_employee_not60, emp_high_positions_comm_allow, \
    emp_not_high_positions_comm_allow, emp_not_high_positions_invalid_comm_allow, no_emp_high_positions_comm_allow, no_emp_not_high_positions_comm_allow, \
    no_emp_not_high_positions_invalid_comm_allow, allowance_with_nomaterial, no_allowance_with_nomaterial = VariableAllowanceInitialization()

    # initilization variable for overtime auditing
    final_summary_regualr_overtime, final_summary_holiday_overtime, not_allowed_overtime, no_final_summary_regualr_overtime, \
    no_final_summary_holiday_overtime, no_not_allowed_overtime = VariableOvertimeInitialization()

    # _________________ When click on start Auditing button ________________
    # create object from requited forms
    master_upload_form, payroll_upload_form = objectFormInitilization()
    selectform_master, selectform_payroll, full_paths_payroll, files_payroll = selectFormInitilization()

    # start Auditing
    if 'directories' in request.form and selectform_master.validate_on_submit():
        # if 'directories_payroll' in request.form and selectform_payroll.validate_on_submit():

        # Fetch selected file from drop down list
        master_file_path = '{}'.format(selectform_master.directories.data)
        # payroll_file_path = '{}'.format(selectform_payroll.directories_payroll.data)
        payroll_file_path = request.form.getlist('mymultiselect')
        if payroll_file_path == []:
            file_path = False
        elif master_file_path == '':
            file_path = False
        elif master_file_path == '' and payroll_file_path == '':
            file_path = False
        else:
            file_path = True

            # global master_df,payroll_df
            # try to import data of the fetched paths if not rise error to notify the user to select path
            global dic_list2
            user_name = str(current_user.username)
            # master_file_path=dic_list2.get(master_file_path)
            master_file_path = secure_join("application", "data", "master_data", user_name, master_file_path)
            master_df, msheetname = Import_Master_Data(master_file_path)

            # ---------------------------------------------------------------------
            """--------- Employee Information Checking and Validation--------- """
            # --------------------------------------------------------------------

            try:
                # Fetch any duplicate name
                duplicate_name = Check_Duplicate_Name(master_df)
                no_duplicate_name = Check_Auditing_Validation(duplicate_name)

                # print(check_car_allowance)
            except Exception as ex:
                value = 'duplicate_name process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True
            try:
                # Fetch any missing name
                missing_name = Check_Missing_Name(master_df)
                no_missing_name = Check_Auditing_Validation(missing_name)
            except Exception as ex:
                value = 'missing_name process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch any invalid cpr
                invalid_CPR = Check_Invalid_CPR(master_df)
                no_invalid_CPR = Check_Auditing_Validation(invalid_CPR)
            except Exception as ex:
                value = 'invalid_CPR process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch any duplicate cpr
                duplicate_cpr = Check_Duplicate_CPR(master_df)
                no_duplicate_cpr = Check_Auditing_Validation(duplicate_cpr)
            except Exception as ex:
                value = 'duplicate_cpr process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch Duplicate account number
                duplicate_acount_no = Check_Duplicate_Accont_No(master_df)
                no_duplicate_acount_no = Check_Auditing_Validation(duplicate_acount_no)
            except Exception as ex:
                value = 'duplicate_acount process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch invalid account number
                invalid_account_no = Check_Invalid_Account_No(master_df)
                no_invalid_account_no = Check_Auditing_Validation(invalid_account_no)
            except Exception as ex:
                value = 'invalid_account process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch invalid Age
                invalid_age = Check_Age(master_df)
                no_invalid_age = Check_Auditing_Validation(invalid_age)
            except Exception as ex:
                value = 'invalid_age process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch who didnt have category
                missing_category = Check_Categories(master_df)
                no_missing_category = Check_Auditing_Validation(missing_category)
            except Exception as ex:
                value = 'missing_category process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch higher annual leave
                invalid_annual = Check_Annual_leave(master_df, msheetname)
                no_invalid_annual = Check_Auditing_Validation(invalid_annual)
            except Exception as ex:
                value = 'invalid_annual process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch higher sick leave
                invalid_sick_leave = Check_Sick_leave(master_df, msheetname)
                no_invalid_sick_leave = Check_Auditing_Validation(invalid_sick_leave)
            except Exception as ex:
                value = 'invalid_sick_leave process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            # try:
            # Fetch if there is two same high ranking position ate the same organization
            duplicate_high_rank_posisiton = Check_High_Rank_Posisiton(master_df)
            no_duplicate_high_rank_posisiton = Check_Auditing_Validation(duplicate_high_rank_posisiton)
            # except Exception as ex:
            #     value = 'duplicate_high_rank_posisiton process has issue in ' + str(
            #         ex) + ' .Please inform technical team'
            #     error1 = True

            try:
                # Fetch if employee has missing_grade
                missing_grade = Missing_GRADE(master_df)
                no_missing_grade = Check_Auditing_Validation(missing_grade)
            except Exception as ex:
                value = 'missing_grade process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                # Fetch if employee has missing_material_status
                missing_material_status = Missing_MARITAL_STATUS(master_df)
                no_missing_material_status = Check_Auditing_Validation(missing_material_status)
            except Exception as ex:
                value = 'missing_material_status process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            # -------------------------------------------------------------------
            # """--------- Employee Deduction Checking and validation --------- """
            # -------------------------------------------------------------------\
            for payroll_file in payroll_file_path:
                payroll_file = secure_join("application", "data", "MonthlyPayroll_data", user_name, payroll_file)
                try:
                    sheetname, payroll_df = Import_Payroll_Data(payroll_file)
                    sheetnames[payroll_file] = sheetname[0]
                except Exception as ex:
                    value = 'Importing payroll file process has issue in ' + str(
                        ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee in master but not in payroll
                    employee_not_in_payroll, employee_not_in_master = Missing_Employee(master_df, payroll_df)
                    no_employee_not_in_payroll = Check_Auditing_Validation(employee_not_in_payroll)
                    no_employee_not_in_master = Check_Auditing_Validation(employee_not_in_master)
                except Exception as ex:
                    value = 'employee_not_in_master process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    invalid_pension_allowance[payroll_file] = Check_Pension_Allowance(master_df, payroll_df)
                    no_invalid_pension_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_pension_allowance[payroll_file])
                except Exception as ex:
                    value = 'invalid_pension_allowance process has issue in ' + str(
                        ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    invalid_social_allowance_deduction[payroll_file] = Check_Social_Allowance_Deduction(master_df,
                                                                                                        payroll_df)
                    no_invalid_social_allowance_deduction[payroll_file] = Check_Auditing_Validation(
                        invalid_social_allowance_deduction[payroll_file])
                except Exception as ex:
                    value = 'invalid_social_allowance_deduction process has issue in ' + str(
                        ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    invalid_unemployment_allowance_deduction[payroll_file] = Check_Unemployment_Allowance_Deduction(
                        master_df, payroll_df)
                    no_invalid_unemployment_allowance_deduction[payroll_file] = Check_Auditing_Validation(
                        invalid_unemployment_allowance_deduction[payroll_file])

                except Exception as ex:
                    value = 'invalid_unemployment_allowance_deduction process has issue in ' + str(
                        ex) + ' .Please inform technical team'
                    error1 = True

                # ------------------------------------------------------------------
                """--------- Employee Allowance Checking and Validation --------- """
                # ------------------------------------------------------------------
                try:
                    # Fetch if employee earn allowance for car and trasport at the same time
                    check_car_allowance[payroll_file] = Check_Car_and_Transport(master_df, payroll_df)
                    no_car_transport_allowance[payroll_file] = Check_Auditing_Validation(
                        check_car_allowance[payroll_file])
                except Exception as ex:
                    value = 'car_transport_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn allowance for Transport not equal 20
                    invalid_transport_allowance[payroll_file] = checkTransportAllowance(master_df, payroll_df)
                    no_invalid_transport_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_transport_allowance[payroll_file])
                except Exception as ex:
                    value = 'transport_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn allowance but didnt have grade
                    allowance_with_nograde[payroll_file] = noGradeWithAllowance(master_df, payroll_df)
                    no_allowance_with_nograde[payroll_file] = Check_Auditing_Validation(
                        allowance_with_nograde[payroll_file])
                except Exception as ex:
                    value = 'allowance_with_no_grade process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn allowance but didnt have material status
                    allowance_with_nomaterial[payroll_file] = noMaterialStatuseWithAllowance(master_df, payroll_df)
                    no_allowance_with_nomaterial[payroll_file] = Check_Auditing_Validation(
                        allowance_with_nomaterial[payroll_file])
                except Exception as ex:
                    value = 'allowance_with_no_material_status process has issue in ' + str(
                        ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn invalid living allowance
                    invalid_living_allowance[payroll_file] = Check_Living_Allowance(master_df, payroll_df)
                    no_living_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_living_allowance[payroll_file])
                except Exception as ex:
                    value = 'living_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn invalid social allowance
                    invalid_social_allowance[payroll_file] = Check_Social_Allowance(master_df, payroll_df)
                    no_invalid_social_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_social_allowance[payroll_file])
                except Exception as ex:
                    value = 'social_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True
                try:
                    # Fetch if employee earn invalid housing allowance
                    invalid_housing_allowance[payroll_file] = Check_Housing_Allowance(master_df, payroll_df)
                    no_invalid_housing_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_housing_allowance[payroll_file])
                except Exception as ex:
                    value = 'housing_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # Fetch if employee earn invalid special allowance
                    invalid_special_allowance[payroll_file] = Check_Special_Allowance(master_df, payroll_df)
                    no_invalid_special_allowance[payroll_file] = Check_Auditing_Validation(
                        invalid_special_allowance[payroll_file])
                except Exception as ex:
                    value = 'special_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:

                    # # Fetch if employee earn invalid car allowance based on position title
                    # # Fetch other employee who earn 60  as car allow
                    # # Fetch other employee who earn any value except 60 or 0 as car allowance
                    invalid_car_allow_position[payroll_file], normal_employee_60[payroll_file], normal_employee_not60[
                        payroll_file] = Check_Car_Allowance(master_df, payroll_df)

                    no_invalid_car_allow_position[payroll_file] = Check_Auditing_Validation(
                        invalid_car_allow_position[payroll_file])
                    no_normal_employee_60[payroll_file] = Check_Auditing_Validation(normal_employee_60[payroll_file])
                    no_normal_employee_not60[payroll_file] = Check_Auditing_Validation(
                        normal_employee_not60[payroll_file])
                except Exception as ex:
                    value = 'car_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

                try:
                    # # Fetch if employee earn invalid communication allowance based on position title, not high position title
                    emp_high_positions_comm_allow[payroll_file], emp_not_high_positions_comm_allow[payroll_file], \
                    emp_not_high_positions_invalid_comm_allow[payroll_file] = Check_Communication_Allowance(master_df,
                                                                                                            payroll_df)

                    no_emp_high_positions_comm_allow[payroll_file] = Check_Auditing_Validation(
                        emp_high_positions_comm_allow[payroll_file])
                    no_emp_not_high_positions_comm_allow[payroll_file] = Check_Auditing_Validation(
                        emp_not_high_positions_comm_allow[payroll_file])
                    no_emp_not_high_positions_invalid_comm_allow[payroll_file] = Check_Auditing_Validation(
                        emp_not_high_positions_invalid_comm_allow[payroll_file])
                except Exception as ex:
                    value = 'Communication_allowance process has issue in ' + str(ex) + ' .Please inform technical team'
                    error1 = True

            # -------------------------------------------------------------------
            """--------- Employee Overtime Checking and validation --------- """
            # -------------------------------------------------------------------
            try:
                final_summary_regualr_overtime, final_summary_holiday_overtime = check_overtime(master_df,
                                                                                                payroll_file_path)
                no_final_summary_regualr_overtime = Check_Auditing_Validation(final_summary_regualr_overtime)
                no_final_summary_holiday_overtime = Check_Auditing_Validation(final_summary_holiday_overtime)

            except Exception as ex:
                value = 'Overtime Auditing process has issue in ' + str(ex) + ' .Please inform technical team'
                error1 = True

            try:
                not_allowed_overtime = notAllowedOvertime(master_df, payroll_file_path)
                no_not_allowed_overtime = Check_Auditing_Validation(not_allowed_overtime)
            except Exception as ex:
                value = 'Not Allowed Overtime Auditing process has issue in ' + str(
                    ex) + ' .Please inform technical team'
                error1 = True

    return render_template('home/index.html', segment="index",
                           ############# Employee Information ##########
                           # return results of check duplicate name
                           no_duplicate_name=no_duplicate_name,
                           duplicate_name_columns=duplicate_name.columns.values,
                           duplicate_name_rows=list(duplicate_name.values.tolist()),
                           # return results of missing name
                           no_missing_name=no_missing_name,
                           missing_name_columns=missing_name.columns.values,
                           missing_name_rows=list(missing_name.values.tolist()),
                           # return results of check invalid cpr
                           no_invalid_CPR=no_invalid_CPR,
                           invalid_CPR_columns=invalid_CPR.columns.values,
                           invalid_CPR_rows=list(invalid_CPR.values.tolist()),
                           # return results of check duplicate cpr
                           no_duplicate_cpr=no_duplicate_cpr,
                           duplicate_cpr_columns=duplicate_cpr.columns.values,
                           duplicate_cpr_rows=list(duplicate_cpr.values.tolist()),
                           # return results of check duplicate account number
                           no_duplicate_acount_no=no_duplicate_acount_no,
                           duplicate_acount_no_columns=duplicate_acount_no.columns.values,
                           duplicate_acount_no_rows=list(duplicate_acount_no.values.tolist()),
                           # return results of check invalid account number
                           no_invalid_account_no=no_invalid_account_no,
                           invalid_account_no_columns=invalid_account_no.columns.values,
                           invalid_account_no_rows=list(invalid_account_no.values.tolist()),
                           # return results of check invalid age
                           no_invalid_age=no_invalid_age,
                           invalid_age_columns=invalid_age.columns.values,
                           invalid_age_rows=list(invalid_age.values.tolist()),
                           # return results of check invalid Annual
                           no_invalid_annual=no_invalid_annual,
                           invalid_annual_columns=invalid_annual.columns.values,
                           invalid_annual_rows=list(invalid_annual.values.tolist()),
                           # return results of check invalid sick leave
                           no_invalid_sick_leave=no_invalid_sick_leave,
                           invalid_sick_leave_columns=invalid_sick_leave.columns.values,
                           invalid_sick_leave_rows=list(invalid_sick_leave.values.tolist()),
                           # return results of check duplicate high ranking
                           no_duplicate_high_rank_posisiton=no_duplicate_high_rank_posisiton,
                           duplicate_high_rank_posisiton_columns=duplicate_high_rank_posisiton.columns.values,
                           duplicate_high_rank_posisiton_rows=list(duplicate_high_rank_posisiton.values.tolist()),
                           # return employee who didnt have category
                           no_missing_category=no_missing_category,
                           missing_category_columns=missing_category.columns.values,
                           missing_category_rows=list(missing_category.values.tolist()),
                           # return results of check missing grade
                           no_missing_grade=no_missing_grade,
                           missing_grade_columns=missing_grade.columns.values,
                           missing_grade_rows=list(missing_grade.values.tolist()),
                           # return results of check missing material status
                           no_missing_material_status=no_missing_material_status,
                           missing_material_status_columns=missing_material_status.columns.values,
                           missing_material_status_rows=list(missing_material_status.values.tolist()),
                           # return employee who are in master but not in payroll
                           no_employee_not_in_master=no_employee_not_in_master,
                           employee_not_in_master_columns=employee_not_in_master.columns.values,
                           employee_not_in_master_rows=list(employee_not_in_master.values.tolist()),
                           # return employee who are in master but not in payroll
                           no_employee_not_in_payroll=no_employee_not_in_payroll,
                           employee_not_in_payroll_columns=employee_not_in_payroll.columns.values,
                           employee_not_in_payroll_rows=list(employee_not_in_payroll.values.tolist()),
                           ################ Deduction ####################
                           # return results of check Pension Allowance
                           no_invalid_pension_allowance=no_invalid_pension_allowance,
                           invalid_pension_allowance=invalid_pension_allowance,
                           # return results of check Social Allowance
                           no_invalid_social_allowance_deduction=no_invalid_social_allowance_deduction,
                           invalid_social_allowance_deduction=invalid_social_allowance_deduction,
                           # return results of check Unemployment Allowance
                           no_invalid_unemployment_allowance_deduction=no_invalid_unemployment_allowance_deduction,
                           invalid_unemployment_allowance_deduction=invalid_unemployment_allowance_deduction,
                           ################ Allowance  ####################
                           # return results of check Car Allowance
                           no_car_transport_allowance=no_car_transport_allowance,
                           check_car_allowance=check_car_allowance,
                           # return results of check living allowance
                           no_living_allowance=no_living_allowance,
                           invalid_living_allowance=invalid_living_allowance,
                           # return results of check social allowance
                           no_invalid_social_allowance=no_invalid_social_allowance,
                           invalid_social_allowance=invalid_social_allowance,
                           # return results of check Housing allowance
                           no_invalid_housing_allowance=no_invalid_housing_allowance,
                           invalid_housing_allowance=invalid_housing_allowance,
                           # return results of check Transport allowance
                           no_invalid_transport_allowance=no_invalid_transport_allowance,
                           invalid_transport_allowance=invalid_transport_allowance,
                           # return any employe have allowance but have no grade
                           no_allowance_with_nograde=no_allowance_with_nograde,
                           allowance_with_nograde=allowance_with_nograde,
                           # return employees who earn allownce without material status
                           allowance_with_nomaterial=allowance_with_nomaterial,
                           no_allowance_with_nomaterial=no_allowance_with_nomaterial,
                           # return invalid special allowance
                           no_invalid_special_allowance=no_invalid_special_allowance,
                           invalid_special_allowance=invalid_special_allowance,
                           # return car allowance auditing results
                           invalid_car_allow_position=invalid_car_allow_position,
                           invalid_car_allow_grade=invalid_car_allow_grade,
                           normal_employee_60=normal_employee_60,
                           normal_employee_not60=normal_employee_not60,
                           no_invalid_car_allow_position=no_invalid_car_allow_position,
                           no_invalid_car_allow_grade=no_invalid_car_allow_grade,
                           no_normal_employee_60=no_normal_employee_60,
                           no_normal_employee_not60=no_normal_employee_not60,
                           # return communication auditing result
                           emp_high_positions_comm_allow=emp_high_positions_comm_allow,
                           emp_not_high_positions_comm_allow=emp_not_high_positions_comm_allow,
                           emp_not_high_positions_invalid_comm_allow=emp_not_high_positions_invalid_comm_allow,
                           no_emp_high_positions_comm_allow=no_emp_high_positions_comm_allow,
                           no_emp_not_high_positions_comm_allow=no_emp_not_high_positions_comm_allow,
                           no_emp_not_high_positions_invalid_comm_allow=no_emp_not_high_positions_invalid_comm_allow,

                           #################### Overtime ##########################
                           # return results for regular overtime auditing results
                           final_summary_regualr_overtime_columns=final_summary_regualr_overtime.columns.values,
                           final_summary_regualr_overtime_rows=list(final_summary_regualr_overtime.values.tolist()),
                           no_final_summary_regualr_overtime=no_final_summary_regualr_overtime,
                           # return results for holiday overtime auditing results
                           final_summary_holiday_overtime_columns=final_summary_holiday_overtime.columns.values,
                           final_summary_holiday_overtime_rows=list(final_summary_holiday_overtime.values.tolist()),
                           no_final_summary_holiday_overtime=no_final_summary_holiday_overtime,
                           # retirn any employee who are taking overtime with grade from E4-E7
                           no_not_allowed_overtime=no_not_allowed_overtime,
                           not_allowed_overtime_rows=list(not_allowed_overtime.values.tolist()),
                           not_allowed_overtime_columns=not_allowed_overtime.columns.values,
                           ###################### othr variables ################
                           # the name of sheets e.g. Housing_Allowance, Living_Allowance
                           sheetnames=sheetnames,
                           # error raising if any issue with uploading the files
                           error=error,
                           # master upload form
                           master_upload_form=master_upload_form,
                           # payroll upload form
                           payroll_upload_form=payroll_upload_form,
                           # dropdown master file name
                           selectform_master=selectform_master,
                           selectform_payroll=selectform_payroll,
                           full_paths_payroll=full_paths_payroll,
                           files_payroll=files_payroll,
                           file_path=file_path,
                           value=value,
                           error1=error1,
                           # Employee information auditing results
                           zip=zip)


######################################################################################-->
#####################Manage Master files page (Deleting files)##############################-->
######################################################################################-->
@blueprint.route('/managefile', methods=["POST", "GET"])
@login_required
def managefile():
    '''Function to load file path of files and delete files by selecting checkbox'''
    selected_file1 = True
    file_deleted1 = False

    """
    # ___________initial fill Table list by file names_____________
    """
    folderName1 = "master_data"
    full_paths1, files1 = GetFileName(folderName1)

    folderName2 = "MonthlyPayroll_data"
    full_paths2, files2 = GetFileName(folderName2)

    full_paths = full_paths1 + full_paths2

    if request.method == 'POST':
        ########### Manage Master File ##########
        if request.form.getlist('checkbox'):
            """if check any checkbox, then set value of no_selected_file to False which means at lease one checkbox is selected"""
            selected_file1 = True
            file_Names1 = request.form.getlist('checkbox')
            for file_name1 in file_Names1:
                # remove selected file
                os.remove(file_name1)
            file_deleted1 = True
        else:
            selected_file1 = False

        # Update the table after delete
        full_paths1, files1 = GetFileName(folderName1)
        full_paths2, files2 = GetFileName(folderName2)
        full_paths = full_paths1 + full_paths2

    return render_template('home/managefiles.html', segment="managefile",
                           full_paths=full_paths,  # all files
                           full_paths1=full_paths1,  # master files
                           full_paths2=full_paths2,  # payroll
                           selected_file1=selected_file1,
                           file_deleted1=file_deleted1,
                           )


######################################################################################-->
######  the excel files sheet employee information auditing results ##################-->
######################################################################################-->
@blueprint.route('/downloadAuditedEmployeeInfo', methods=['GET', 'POST'])
@login_required
def downloadAuditedEmployeeInfo():
    """Call function to Generte Excel report for Employee information Auditing Results"""
    if request.form.getlist('switchedOn'):
        # list_swichedon_values = request.form.getlist('switchedOn')
        # print(list_swichedon_values)
        file_name = "Employee_Information"
        Prepare_Employee_Information_report(master_df, file_name, msheetname,payroll_df)

        # For windows you need to use drive name [ex: F:/Example.pdf]
        path = file_path + file_name + '_Auditing_Result_Report.xlsx'

    return send_file(path, as_attachment=True)


######################################################################################-->
######  the excel files sheet deduction auditing results ##################-->
######################################################################################-->
@blueprint.route('/downloadAuditedDeduction', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def downloadAuditedDeduction():
    """Call function to Generte Excel report for Employee information Auditing Results"""
    if request.form.getlist('switchedOn'):
        # list_swichedon_values = request.form.getlist('switchedOn')
        # print(list_swichedon_values)
        file_name = "Employee_Deduction"
        Prepare_Employee_Deduction_report(master_df, payroll_file_path, file_name)

        # For windows you need to use drive name [ex: F:/Example.pdf]
        path = file_path + file_name + '_Auditing_Result_Report.xlsx'
    return send_file(path, as_attachment=True)


######################################################################################-->
######  the excel files sheet allowance auditing results ##################-->
######################################################################################-->
@blueprint.route('/downloadAuditedAllowanmce', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def downloadAuditedAllowanmce():
    """Call function to Generte Excel report for Employee information Auditing Results"""
    if request.form.getlist('switchedOn'):
        # list_swichedon_values = request.form.getlist('switchedOn')
        # print(list_swichedon_values)
        file_name = "Employee_Allowance"
        Prepare_Employee_Allowance_report(master_df, payroll_file_path, file_name)

        # For windows you need to use drive name [ex: F:/Example.pdf]

        path = file_path + file_name + '_Auditing_Result_Report.xlsx'
    return send_file(path, as_attachment=True)


######################################################################################-->
######  the excel files sheet Overtime auditing results ##################-->
######################################################################################-->
@blueprint.route('/downloadAuditedEmployeeOvertime', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def downloadAuditedEmployeeOvertime():
    path = ''
    file_name = "Employee_Overtime"
    """Call function to Generte Excel report for Employee information Auditing Results"""
    if request.form.getlist('switchedOn'):
        # list_swichedon_values = request.form.getlist('switchedOn')
        Prepare_Employee_Overtime_report(master_df, payroll_file_path, file_name)
        # For windows you need to use drive name [ex: F:/Example.pdf]
        path = file_path + file_name + '_Auditing_Result_Report.xlsx'
    # if path == '':
    #     gen_report_path = generate_report_path()
    #     path = gen_report_path + file_name + '_Auditing_Result_Report.xlsx'
    #     pass
    # else:
    return send_file(path, as_attachment=True)


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except Exception as ex:
        print(ex)
        return render_template('home/page-400.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except Exception as ex:
        print(ex)
        return None


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('home/page-400.html', reason=e.description), 400
