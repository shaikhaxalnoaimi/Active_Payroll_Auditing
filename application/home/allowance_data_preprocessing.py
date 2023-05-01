"""
File Name: application\home\allowance_data_preprocessing.py

Purpose: This file contains functions to audit employee allowances in payroll data. It checks for discrepancies in car and transport allowance, transport allowance, living allowance, social allowance, housing allowance, special allowance, car allowance, and communication allowance.

Dependencies:

pandas (version 1.2.4)
numpy (version 1.20.1)
openpyxl (version 3.0.7)
xlsxwriter (version 1.3.8)
sqlalchemy (version 1.4.7)
Code Structure:

Import necessary libraries
Define functions:
Import_Payroll_Data: imports payroll data from an excel file
Organize_Data_View: organizes data view for better readability
generate_report_path: generates the path for the report file
organized_allowance_file: generates the path for the allowance file
fetchAllPositionTitle: fetches all high ranking positions from the database
Check_Car_and_Transport: checks for discrepancies in car and transport allowance
checkTransportAllowance: checks for discrepancies in transport allowance
noGradeWithAllowance: checks for discrepancies in allowance for employees without a grade
noMaterialStatuseWithAllowance: checks for discrepancies in allowance for employees without a material status
Check_Living_Allowance: checks for discrepancies in living allowance
Check_Social_Allowance: checks for discrepancies in social allowance
Check_Housing_Allowance: checks for discrepancies in housing allowance
Check_Special_Allowance: checks for discrepancies in special allowance
Check_Car_Allowance: checks for discrepancies in car allowance
normalEmployeeCarAllow: fetches employees who are not in high position and not in J grade that have 60 as car allowance and employees who are not in high position and not in J grade that have other value than 60 or 0 as car allowance
Check_Communication_Allowance: checks for discrepancies in communication allowance
Prepare_Employee_Allowance_report: prepares an excel report of employee allowance auditing results


"""


import pandas as pd
from application import generate_report_path, generate_allowancefile_path, organized_allowance_file
from application.Control_Panel.position_titles_db_Quires import fetchAllPositionTitle
from application.home.data_processing import Organize_Data_View, Unicode_Column_Names, Import_Payroll_Data



""":
--------------------------------------------------------------------------------------------------------------------------------------
__________________________________________________ Preprocessing the Allowance files _________________________________________________
The below function responsible to fetch Living,Housing,Social,Special,Car, and communication allowance data (based on selected path-should be dynamic in the future)
--------------------------------------------------------------------------------------------------------------------------------------
"""
def Fetch_Living_Housing_Special_Allowance_Data(df):
    """
    This function will be called several time with different df each df represent different sheet (social, living or housing)
    The function will check the number of headers if more than one header will do process if less then one header will do another process
    Parameters
    ----------
    df
    allowance df (social, living or housing)

    Returns
    -------
    organized allowance_df but with missing grade and level these two columns will be processed in different function called Add_Grade_Allowance(allowance_df)

    """
    # df = pd.read_excel('/NAO-Payroll/application/data/AllowanceFiles/Allowances Tables - English (1).xlsx', sheet_name='Housing Allowance', header=[0, 1])

    # Remove unicode character from column names
    df = Unicode_Column_Names(df)

    # Num of Rows
    rows = len(df)
    # Num of Cols
    cols = len(df.columns)
    # list of columns Name
    col_name = list(df.columns.values)
    #col_name[0][0]

    if df.columns.nlevels > 1:
        allowance_df = pd.DataFrame(columns=['Level', 'AllowanceType','Status' ,'Allowance_Values','Grade_Letter','Grade'])
        gradeNumber = 0
        for Grade in range(0, rows):
            j = 0 #columns name (Diplomacy, Diplomacy,Educational,Educational,..... )
            gradeNumber = gradeNumber+1
            # to iterate from 1 to 10
            for allowance_type in range(0, cols - 1):
                #print(gradeNumber, col_name[j][0], col_name[j][1], df.iloc[Grade, allowance_type])
                dict_list = [{'Level':gradeNumber, 'AllowanceType':col_name[j][0], 'Status':col_name[j][1], 'Allowance_Values':df.iloc[Grade, allowance_type], 'Grade_Letter':"","Grade":""}]
                allowance_df = pd.concat([allowance_df, pd.DataFrame.from_records(dict_list)])
                j = j + 1

        # Replace column value (it will be applied on social allowance )
        allowance_df['Status'] = allowance_df['Status'].replace('Married', 'Married|Divorce|Widowed')
        allowance_df['Status'] = allowance_df['Status'].replace('Married with two or more children', 'Married|Divorce|Widowed')
        allowance_df['Status'] = allowance_df['Status'].replace('married without children', 'Married|Divorce|Widowed')
    else:
        allowance_df = pd.DataFrame(columns=['Level', 'AllowanceType', 'Allowance_Values', 'Grade_Letter', 'Grade'])
        gradeNumber = 0
        for Grade in range(0, rows):
            gradeNumber = gradeNumber + 1
            #print(Grade)
            # to iterate from 1 to 10
            for allowance_type in range(0, cols - 1):
                #print(allowance_type)
                # print(gradeNumber, col_name[j][0], col_name[j][1], df.iloc[Grade, allowance_type])
                dict_list = [{'Level': gradeNumber, 'AllowanceType': col_name[allowance_type], 'Allowance_Values': df.iloc[Grade, allowance_type], 'Grade_Letter': "", "Grade": ""}]
                allowance_df = pd.concat([allowance_df, pd.DataFrame.from_records(dict_list)])

    return allowance_df



def Add_Grade_Allowance(allowance_df):
    """
    This function will add the grade based on level for example if (Diplomacy add D, if Educational add A) these leve will be applied for all grade from 1 to 10
    Parameters
    ----------
    allowance_df
        organized allowance_df but with missing grade and level

    Returns
    -------
    allowance_df
        final organized allowance dfs (social, housing and living)
    """

    allowanceGrades = allowance_df['AllowanceType'].unique()

    for allowanceGrade in allowanceGrades:
        if 'Diplomacy' in allowanceGrade:
            # print(allowanceGrade)
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "D"
        if 'Educational' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "A"
        if 'Executive' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "E"
        if 'Judges' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "J"
        if 'Specialist' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "P"
        if 'General' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "G"
        if 'legal' in allowanceGrade:
            allowance_df['Grade_Letter'][allowance_df['AllowanceType'] == allowanceGrade] = "L"

    #convert leve to string and combine lever + Grade_letter to get Grade with matching with master data
    allowance_df['Level'] = allowance_df['Level'].astype(str)
    allowance_df['Grade'] = allowance_df[['Grade_Letter', 'Level']].agg(''.join, axis=1)

    return allowance_df




def Fetch_Allow_SheetNames():
    """
    This function to read the standard allowance table  to access their sheet names
    Returns
    -------
    allowance_fnames:
        sheetnames as list
    """
    file_path = generate_allowancefile_path()
    # xls_file = pd.ExcelFile('/NAO-Payroll/application/data/AllowanceFiles/Allowances Tables - English (1).xlsx')
    xls_file = pd.ExcelFile(file_path+'/Allowances Tables - English (1).xlsx')
    # allowance_fnames = [sheet for sheet in xls_file.sheet_names] Unnecessary use of a comprehension, use list(xls_file.sheet_names) instead. (128:23) [unnecessary-comprehension]
    allowance_fnames= xls_file.sheet_names
    return  allowance_fnames

def Process_Allowance_Table():
    """
    This function to preprocess the Housing, Living , and Social allowance. The file stored in specific location this file has three sheets
    two sheets have two headers name (Social, Housing) one header for level such as (educational, executive, ...) and other headder for material status such as (married, single, ..)
    the third sheet has only one header so need to be processed in different way, so if condition is required as shown below code

    Output
    ------
    Exported  three  final organized excel sheets for 'Living Allownce', 'Socail Allowance', 'Housing Allowance' in main diractory of this projects
    these file can be used to auditing these allwance by comparing them with payroll file connected with master by cpr
    """

    # access sheet names
    allowance_fnames = Fetch_Allow_SheetNames()

    #allowance_fname='Living Allownce'
    file_path = generate_allowancefile_path()
    org_file_path = organized_allowance_file()
    for allowance_fname in allowance_fnames:
        if 'Living' in allowance_fname:
            df = pd.read_excel(file_path+'/Allowances Tables - English (1).xlsx',sheet_name=allowance_fname) # only one header
        else:
            df = pd.read_excel(file_path+'/Allowances Tables - English (1).xlsx', sheet_name = allowance_fname, header=[0, 1]) # has two headr

        allowance_df = Fetch_Living_Housing_Special_Allowance_Data(df)  # Preprocessing and preparing the data to use them in allowance auditing (living,housing,Social)
        allowance_df = Add_Grade_Allowance(allowance_df)  # add grade allowance based on level and allowance type
        # replace - by 0
        allowance_df["Allowance_Values"] = allowance_df["Allowance_Values"].replace("-", "0", regex=True)
        # fill null by 0
        allowance_df["Allowance_Values"] = allowance_df["Allowance_Values"].fillna(0)
        # convert LIVING_STD to float
        allowance_df['Allowance_Values'] = allowance_df['Allowance_Values'].astype('float64')

        # this condition will applied only for housing allowance
        # merging the married with child and married with two child as one row and combine allowance value
        if allowance_fname == 'Housing Allowance':
            # print(allowance_fname)
            # allowance_df = pd.read_excel('/NAO-Payroll/application/data/Organized Allowance Files/Housing Allowance.xlsx')
            # allowance_fname = 'Housing Allowance'
            allowance_df["Allowance_Values"] = allowance_df["Allowance_Values"].astype(int)
            allowance_df["Allowance_Values"] = allowance_df["Allowance_Values"].astype(str)
            allowance_df = allowance_df.groupby(["Level", 'Grade', 'Status', "AllowanceType", "Grade_Letter"])['Allowance_Values'].apply('|'.join).reset_index()

        allowance_df.to_excel(org_file_path + '/'+allowance_fname + '.xlsx',index=False)
        #allowance_df[allowance_df['Grade_Letter']=='D'][['Grade','Level','AllowanceType']]


"""
#--------------------------------------------------------------------------------------------------------------------------------------
# Below function called once to generate Social, Housing , Living Allowance tables
 (if we removed the generated file for any reason we need to call this function again)
#--------------------------------------------------------------------------------------------------------------------------------------
"""
# Process_Allowance_Table()

""":
--------------------------------------------------------------------------------------------------------------------------------------
____________________________________________________ Auditing Allowance Process ______________________________________________________
The below function responsible to fetch Car, Living,Housing,and Social allowance data (based on selected path-should be dynamic in the future)
--------------------------------------------------------------------------------------------------------------------------------------
"""


#_________________________ Check Car & Transport Allowance________________
def Check_Car_and_Transport(df_master,df_payroll):
    filtred_master_df = df_master[['CPR_NO', 'EMPLOYEE_NAME', 'POSITION_TITLE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)

    # df_payroll = pd.read_excel('/NAO-Payroll/application/data/MonthlyPayroll_data/admin/payroll-30082022_094926.xlsx')
    filtred_payroll_df = df_payroll[['CPR_NO','CAR_ALLOW','TRANSPORT_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)


    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    merged_df = merged_df.round({'CAR_ALLOW': 3})
    merged_df = merged_df.round({'TRANSPORT_ALLOW': 3})

    check_car_allowance = merged_df[(merged_df['CAR_ALLOW'] > 0) & (merged_df['TRANSPORT_ALLOW'] > 0)]
    check_car_allowance = check_car_allowance[[ 'CPR_NO', 'POSITION_TITLE', 'CAR_ALLOW', 'TRANSPORT_ALLOW']]

    # to show data in organized way
    # check_car_allowance = Organize_Data_View(check_car_allowance)

    return check_car_allowance

#_________________________ Check value of Transport Allowance________________
def checkTransportAllowance(df_master,df_payroll):
    """

    Parameters
    ----------
    df_master
        employee master df to fetch the employee information
    df_payroll
        employee payroll df to check 'Car' allowance


    Returns
    -------
        any employee that has transport more than 20
    """
    # import pandas as pd
    # df_master = pd.read_excel('C:/nao-payroll-deployment-dock/NAO-Payroll/application/data/master_data/admin/Master_as_of_July-_with_error-04102022_102708.xlsx')
    filtred_master_df = df_master[['CPR_NO', 'EMPLOYEE_NAME', 'POSITION_TITLE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)

    # df_payroll = pd.read_excel('C:/nao-payroll-deployment-dock/NAO-Payroll/application/data/MonthlyPayroll_data/admin/Jul-2022-Pay_Report-04102022_102945.xlsx')
    filtred_payroll_df = df_payroll[['CPR_NO','CAR_ALLOW','TRANSPORT_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    merged_df = merged_df.round({'CAR_ALLOW': 3})
    merged_df = merged_df.round({'TRANSPORT_ALLOW': 3})

    check_Transport_allowance = merged_df[(merged_df['CAR_ALLOW'] == 0.0) & (merged_df['TRANSPORT_ALLOW'] != 0.0 )]
    check_Transport_allowance =  check_Transport_allowance[(check_Transport_allowance['TRANSPORT_ALLOW'] != 20.0 )]
    check_Transport_allowance = check_Transport_allowance[[ 'CPR_NO', 'POSITION_TITLE', 'CAR_ALLOW', 'TRANSPORT_ALLOW']]

    # to show data in organized way
    # check_Transport_allowance = Organize_Data_View(check_Transport_allowance)
    # print(check_Transport_allowance)
    return check_Transport_allowance

def noGradeWithAllowance(df_master, df_payroll):
    """
    This function will fetch all employees who earn social,living,housing,or car allowance but at the same time they dont have grade
    note: any employee didnt have grade should not have above allowance that is the main purpose of the function
    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'LIVING_STD','SOCIAL', 'Housing' allowance

    Returns
    -------
        Audit result for Living, Housing, and Social Allowance each one should check all level and grade

    """
    # filter df
    filtred_master_df = df_master[['CPR_NO', 'POSITION_TITLE', 'GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','LIVING_STD_ALLOW','SOCIAL_ALLOW','HOUSING_ALLOW','CAR_ALLOW','SPECIAL_ALLOW','COMMUNICATION_ALLOW','TRANSPORT_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

    if not merged_df.empty:
        org_file_path = organized_allowance_file()
        # read standard grade file
        standard_grade_df = pd.read_excel(org_file_path + '/Standard Grade.xlsx')
        standard_grade_df = standard_grade_df[standard_grade_df['Grade'] != 'N']
        # join the lise valu using | character
        join_grade = '|'.join(standard_grade_df['Grade'].tolist())

        allow_without_grade = merged_df[~(merged_df['GRADE'].str.contains(join_grade, na=False, case=False, regex=True)) & ( (merged_df['LIVING_STD_ALLOW'] != 0.0) | (merged_df['SOCIAL_ALLOW'] != 0.0) | (merged_df['HOUSING_ALLOW'] != 0.0) |  (merged_df['CAR_ALLOW'] != 0.0) | (merged_df['SPECIAL_ALLOW'] != 0.0) | (merged_df['COMMUNICATION_ALLOW'] != 0.0)  | (merged_df['TRANSPORT_ALLOW'] != 0.0)  )]

        # get the missing data of LIVING_STD
        # allow_without_grade= merged_df[((merged_df['GRADE'] == "_") |(merged_df['GRADE'] == "N") ) &  ( (merged_df['LIVING_STD_ALLOW'] != 0.0) | (merged_df['SOCIAL_ALLOW'] != 0.0) | (merged_df['HOUSING_ALLOW'] != 0.0) |  (merged_df['CAR_ALLOW'] != 0.0))][['CPR_NO','GRADE','LIVING_STD_ALLOW','SOCIAL_ALLOW','HOUSING_ALLOW','CAR_ALLOW']]
        # allow_without_grade = Organize_Data_View(allow_without_grade)
    else:
        allow_without_grade = pd.DataFrame(columns = ['CPR_NO','GRADE','LIVING_STD_ALLOW','SOCIAL_ALLOW','HOUSING_ALLOW','CAR_ALLOW'])

    return allow_without_grade


def noMaterialStatuseWithAllowance(df_master, df_payroll):
    """
    This function will fetch all employees who earn social,housing allowance but at the same time they have missing material status
    note: any employee didnt have material status should not have above allowance that is the main purpose of the function
    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'LIVING_STD','SOCIAL', 'Housing' allowance

    Returns
    -------
        Audit result for Living, Housing, and Social Allowance each one should check all level and grade

    """

    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE', 'MARITAL_STATUS']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','SOCIAL_ALLOW','HOUSING_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

    if not merged_df.empty:
        # get the missing data of LIVING_STD
        allow_without_grade= merged_df[(merged_df['MARITAL_STATUS'] == "_") &  ( (merged_df['SOCIAL_ALLOW'] != 0) | (merged_df['HOUSING_ALLOW'] != 0) )][['CPR_NO','MARITAL_STATUS','SOCIAL_ALLOW','HOUSING_ALLOW']]
    else:
        allow_without_grade = pd.DataFrame(columns = ['CPR_NO','POSITION_TITLE','MARITAL_STATUS','SOCIAL_ALLOW','HOUSING_ALLOW'])

    return allow_without_grade

def Check_Living_Allowance(df_master, df_payroll):
    """
    Below function to call function Process_Allowance_Table() to prepare Living,Housing and social external tables and then export them as excel
    after that will import each one in a separate df to audit Living, Housing, and Social Allowance.
    this function will be responsible to auditing living allowance

    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'LIVING_STD','SOCIAL', 'Housing' allowance

    Returns
    -------
        Audit result for Living, Housing, and Social Allowance each one should check all level and grade
    """
    # prepare allowance table and save them in project file (future these files will be saved in db)

    # fetch sheet names to represent allowance type
    allowance_fnames = Fetch_Allow_SheetNames()
    org_file_path = organized_allowance_file()


    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE', 'GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','LIVING_STD_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

    if not merged_df.empty:
        # Import generated living table ([0] index for living file)
        living_df = pd.read_excel(org_file_path + '/'+ allowance_fnames[0] + '.xlsx')
        # Fetch standard living allowance grade
        grades = list(living_df['Grade'].values)
        # Fetch standard living allowance values
        values = list(living_df['Allowance_Values'].values)
        # df to store (concat) all results of auditing living files
        living_grade = pd.DataFrame()

        # Check grade and check the amount for the grade if correct
        for i in range(len(grades)):
            # match the grade of merged df and allowance df together (note: if merged df didnt have grage then will never match with any grade)
            living_grade_in_merged_df = merged_df[(merged_df['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))][[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'LIVING_STD_ALLOW']]

            # detect if LIVING_STD_ALLOW in payroll not equal to the standard living allowance (both values should equal otherwise will be detected)
            detected_living_allowance = living_grade_in_merged_df[(living_grade_in_merged_df['LIVING_STD_ALLOW'] != values[i])]

            # fetch any values from master not match with values in living allowance
            if not detected_living_allowance.empty:
                # print(values[i])
                #Append results in new df named living_grade
                living_grade = pd.concat([detected_living_allowance, living_grade])


        # living_grade= Organize_Data_View(living_grade)
        if not living_grade.empty:
            # Fetching the matched actual grades and values with the auditing summary results (living_grade df) that has non matched living allowance
            actual_grades = []
            actual_values =[]
            for i in range(len(grades)):
                test = living_grade[(living_grade['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))][['GRADE','LIVING_STD_ALLOW']]
                if not test.empty:
                    actual_grades.append(grades[i])
                    actual_values.append(values[i])

            # extract grades shortcut from GRADE using regular expression to be able to match them with extracted list
            living_grade['Grade_Shortcut'] = living_grade['GRADE'].str.extract(r"([a-zA-Z][0-9]+)",expand=False)

            # add the new column for actual living allowance values and matching them using grade
            count = 0
            for actual_grade in actual_grades:
                living_grade.loc[living_grade['Grade_Shortcut'] == actual_grade, 'ALLOW_AP_CSB'] = actual_values[count]
                count = count +1

            living_grade["ALLOW_AP_CSB"] = living_grade["ALLOW_AP_CSB"].astype(int)
            # drop the shortcut column for grade after matching
            living_grade = living_grade.drop(['Grade_Shortcut'],axis=1)
            #
            # living_grade.to_excel('livingGrade.xlsx')
            # merged_df.to_excel('merged_df.xlsx')
        else:
            living_grade = pd.DataFrame(
                columns=[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'LIVING_STD_ALLOW',
                         'ALLOW_AP_CSB'])
    else:

        living_grade = pd.DataFrame(columns= [ 'CPR_NO', 'POSITION_TITLE', 'GRADE','LIVING_STD_ALLOW','ALLOW_AP_CSB','SPECIAL_ALLOW','COMMUNICATION_ALLOW','TRANSPORT_ALLOW'])

    # to ensure and confirm there is no any LIVING_STD_ALLOW equal ALLOW_AP_CSB
    if not living_grade.empty:
        living_grade = living_grade[living_grade['LIVING_STD_ALLOW'] != living_grade['ALLOW_AP_CSB']]
    return living_grade




def Check_Social_Allowance(df_master, df_payroll):
    """
    This function will be responsible to auditing Social Allowance.
    How the function work first will filter required columns from master and payroll then merged both dfs by CPR_no
    After that will check if there is any social allowance not follow the standard
    Examples:
    __________
    Grade == Material status = matching values
    D1 ==> single or marred or divorce ==> if single value should =  50
                                           if married or divorce value should = 32

    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'LIVING_STD','SOCIAL', 'Housing' allowance

    Returns
    -------
        Audit result for Social Allowance
    """

    # received master and payroll file
    # df_master = pd.read_excel('../NAO-Payroll/application/data/master_data/admin/Database_Jan_2021-_S-10092022_171202.xlsx')
    # df_payroll = pd.read_excel('../NAO-Payroll/application/data/MonthlyPayroll_data/admin/Jan-2022-payroll-05092022_135455.xlsx')
    org_file_path = organized_allowance_file()
    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'MARITAL_STATUS']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','SOCIAL_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    # merged_df = Missing_GRADE(merged_df)
    # merged_df = Missing_MARITAL_STATUS(merged_df)
    # merged_df = Organize_Data_View(merged_df)
    if not merged_df.empty:
        # Dropping the missing LIVING_STD_ALLOW because it will shows in missing living_std table (no need to auditing them)
        # df= df.dropna(subset=['GRADE'])


        # fetch sheet names to represent allowance type
        allowance_fnames = Fetch_Allow_SheetNames()

        # Import generated living table ([0] index for living file)
        social_df = pd.read_excel(org_file_path + '/'+ allowance_fnames[1] + '.xlsx')
        # Fetch standard living allowance grade
        grades = list(social_df['Grade'].values)
        # Fetch standard living allowance values
        values = list(social_df['Allowance_Values'].values)
        # Fetch material Status
        mstatus = list(social_df['Status'].values)

        # remove spaces if any
        merged_df['MARITAL_STATUS'] = merged_df['MARITAL_STATUS'].str.strip()

        # df to store (concat) all results of auditing living files
        social_grade = pd.DataFrame()


        # Check grade and check the amount for the grade if correct
        for i in range(len(grades)):
            # match the grade of merged df and allowance df together (note: if merged df didnt have grage then will never match with any grade)
            social_grade_in_merged_df = merged_df[(merged_df['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))][['CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'SOCIAL_ALLOW']]

            # detect if SOCIAL_ALLOW in payroll not equal to the standard SOCIAL allowance (both values should equal otherwise will be detected) take material status into consideration
            detected_social_allowance = social_grade_in_merged_df[(social_grade_in_merged_df['SOCIAL_ALLOW'] != values[i]) & social_grade_in_merged_df['MARITAL_STATUS'].str.contains(mstatus[i], na=False, case=False, regex=True ) ]

            # fetch any values from master not match with values in living allowance
            if not detected_social_allowance.empty:
                # Append results in new df named living_grade
                social_grade = pd.concat([detected_social_allowance, social_grade])

        # social_grade= Organize_Data_View(social_grade)
        if not social_grade.empty:
            # Fetching the matched actual grades and values with the auditing summary results (living_grade df) that has non matched living allowance
            actual_grades = []
            actual_values =[]
            actual_status = []
            for i in range(len(grades)):
                match_social_grade = social_grade[(social_grade['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))]
                if not match_social_grade.empty:
                    actual_grades.append(grades[i])
                    actual_values.append(values[i])
                    actual_status.append(mstatus[i])

            # extract grades shortcut from GRADE using regular expression to be able to match them with extracted list
            social_grade['Grade_Shortcut'] = social_grade['GRADE'].str.extract(r"([a-zA-Z][0-9]+)",expand=False)

            # add the new column for actual living allowance values and matching them using grade and material status
            count = 0
            for actual_grade in actual_grades:
                social_grade.loc[(social_grade['Grade_Shortcut'] == actual_grade) & social_grade['MARITAL_STATUS'].str.contains(actual_status[count], na=False, case=False, regex=True ) , 'ALLOW_AP_CSB'] = actual_values[count]

                # social_grade.loc[social_grade['MARITAL_STATUS'] == actual_status, 'Actual_Status'] = actual_status[count]
                count = count +1

            social_grade["ALLOW_AP_CSB"] = social_grade["ALLOW_AP_CSB"].astype(int)
            # drop the shortcut column for grade after matching
            social_grade = social_grade.drop(['Grade_Shortcut'],axis=1)
            #
            # social_grade.to_excel('social_grade.xlsx')
            # merged_df.to_excel('merged_df.xlsx')
        else:
            social_grade = pd.DataFrame(
                columns=[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'MARITAL_STATUS', 'SOCIAL_ALLOW',
                         'ALLOW_AP_CSB'])
    else:
        social_grade = pd.DataFrame(
            columns=[ 'CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'SOCIAL_ALLOW', 'ALLOW_AP_CSB'])

    # to ensure and confirm there is no any LIVING_STD_ALLOW equal ALLOW_AP_CSB
    if not social_grade.empty:
        social_grade = social_grade[social_grade['SOCIAL_ALLOW'] != social_grade['ALLOW_AP_CSB']]
    return social_grade








def Check_Housing_Allowance(df_master, df_payroll):
    """
    This function will be responsible to auditing Housing Allowance.
    How the function work first will filter required columns from master and payroll then merged both dfs by CPR_no
    After that will check if there is any social allowance not follow the standard
    Examples:
    __________
    Grade == Material status = matching values
    L1 ==> single or marred with two children or  ==> if single value should =  100
                                                      if Married with two or more children value should = 250
                                                      if married without children value should = 200

    Note: in master there is no column mentioned details about how many children so will check if contains married
          if yes check value twice one for more than two and one for one child if different then show it in auditing result

    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'Housing' allowance

    Returns
    -------
        Audit result for Housing Allowance
    """

    # received master and payroll file
    # df_master = pd.read_excel('/NAO-Payroll/application/data/master_data/admin/Database_Jan_2021-_S-05092022_135309.xlsx')
    # df_payroll = pd.read_excel('/NAO-Payroll/application/data/MonthlyPayroll_data/admin/Jan-2022-payroll-05092022_135455.xlsx')


    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'MARITAL_STATUS','NATIONALITY']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','HOUSING_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    org_file_path = organized_allowance_file()
    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    if not merged_df.empty:
        # Dropping the missing LIVING_STD_ALLOW because it will shows in missing living_std table (no need to auditing them)
        # df= df.dropna(subset=['GRADE'])

        #  convert HOUSING_ALLOW to str because allowance values standard are string
        merged_df['HOUSING_ALLOW'] = merged_df['HOUSING_ALLOW'].astype('str')
        # remove spaces if any
        merged_df['HOUSING_ALLOW'] = merged_df[ 'HOUSING_ALLOW'].str.strip()

        # fetch sheet names to represent allowance type
        allowance_fnames = Fetch_Allow_SheetNames()

        # Import generated HOUSITNG table ([2] index for Housing file)
        social_df = pd.read_excel(org_file_path + '/'+ allowance_fnames[2] + '.xlsx')
        # Fetch standard living allowance grade
        grades = list(social_df['Grade'].values)
        # Fetch standard living allowance values
        values = list(social_df['Allowance_Values'].values)
        # Fetch material Status
        mstatus = list(social_df['Status'].values)




        # df to store (concat) all results of housing auditing
        housing_grade = pd.DataFrame()
        # Check grade and check the amount for the grade if correct
        for i in range(len(grades)):
            # match the grade of merged df and allowance df together (note: if merged df didnt have grage then will never match with any grade)
            housing_grade_in_merged_df = merged_df[(merged_df['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))][[ 'CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'HOUSING_ALLOW','NATIONALITY']]

            # detect if SOCIAL_ALLOW in payroll not equal to the standard SOCIAL allowance (both values should equal otherwise will be detected) take material status into consideration
            detected_housing_allowance = housing_grade_in_merged_df[(~housing_grade_in_merged_df['HOUSING_ALLOW'].str.contains(str(values[i]), na=False, case=False, regex=True)) & housing_grade_in_merged_df['MARITAL_STATUS'].str.contains(mstatus[i], na=False, case=False, regex=True) ]
            # print(housing_grade_in_merged_df)
            # fetch any values from master not match with values in living allowance
            if not detected_housing_allowance.empty:
                # Append results in new df named living_grade
                housing_grade = pd.concat([detected_housing_allowance, housing_grade])


        # housing_grade= Organize_Data_View(housing_grade)
        if not housing_grade.empty:
            # Fetching the matched actual grades and values with the auditing summary results (living_grade df) that has non matched living allowance
            actual_grades = []
            actual_values =[]
            actual_status = []
            for i in range(len(grades)):
                match_social_grade = housing_grade[(housing_grade['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))]
                if not match_social_grade.empty:
                    actual_grades.append(grades[i])
                    actual_values.append(values[i])
                    actual_status.append(mstatus[i])

            # extract grades shortcut from GRADE using regular expression to be able to match them with extracted list
            housing_grade['Grade_Shortcut'] = housing_grade['GRADE'].str.extract(r"([a-zA-Z][0-9]+)",expand=False)

            # add the new column for actual housing allowance values and matching them using grade and material status
            count = 0
            for actual_grade in actual_grades:
                housing_grade.loc[(housing_grade['Grade_Shortcut'] == actual_grade) & housing_grade['MARITAL_STATUS'].str.contains(actual_status[count], na=False, case=False, regex=True ) , 'ALLOW_AP_CSB'] = actual_values[count]

                # social_grade.loc[social_grade['MARITAL_STATUS'] == actual_status, 'Actual_Status'] = actual_status[count]
                count = count +1

            # housing_grade["ALLOW_AP_CSB"] = housing_grade["ALLOW_AP_CSB"].astype(int)

            # drop the shortcut column for grade after matching
            housing_grade = housing_grade.drop(['Grade_Shortcut'],axis=1)
        #
        # housing_grade.to_excel('housing_grade.xlsx')
        # merged_df.to_excel('merged_df.xlsx')
        else:
            housing_grade = pd.DataFrame(
                columns=[ 'CPR_NO', 'POSITION_TITLE', 'GRADE', 'MARITAL_STATUS', 'HOUSING_ALLOW','ALLOW_AP_CSB', 'NATIONALITY'])
    else:
        housing_grade =  pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'HOUSING_ALLOW', 'ALLOW_AP_CSB','NATIONALITY'])

    if not housing_grade.empty:
        # (Housing allowance) should be linked to Nationality (it is only for non-Bahrainis )
        housing_grade = housing_grade[(housing_grade['NATIONALITY'] != 'BAHRAINI') ][[ 'CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'HOUSING_ALLOW', 'ALLOW_AP_CSB','NATIONALITY']]
    #     # that do not receive a lump sum amount i.e his/her grade is not (N).
    #     housing_grade = housing_grade[ housing_grade['GRADE'] != 'N']
    return housing_grade




def Check_Special_Allowance(df_master, df_payroll):
    """
    This function will be responsible to auditing Special Allowance.
    How the function work first will filter required columns from master and payroll then merged both dfs by CPR_no
    After that will check if there is any special allowance not follow the standard
    checking process depend on position_title
    Examples:
    __________
   UNDERSECRETARY  | PRESIDENT ==> should have allowance (750)


    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check 'LIVING_STD','SOCIAL', 'Housing' allowance

    Returns
    -------
        Audit result for Special Allowance
    """

    # received master and payroll file
    # df_master = pd.read_excel('../NAO-Payroll/application/data/master_data/admin/Database_Jan_2021-_S-10092022_171202.xlsx')
    # df_payroll = pd.read_excel('../NAO-Payroll/application/data/MonthlyPayroll_data/admin/Jan-2022-payroll-05092022_135455.xlsx')


    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE','GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','SPECIAL_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    org_file_path = organized_allowance_file()
    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

    if not merged_df.empty:
        # Dropping the missing LIVING_STD_ALLOW because it will shows in missing living_std table (no need to auditing them)
        # df= df.dropna(subset=['GRADE'])

        #  convert LIVING_STD_ALLOW to float
        merged_df['SPECIAL_ALLOW'] = merged_df['SPECIAL_ALLOW'].fillna(0)
        merged_df['SPECIAL_ALLOW'] = merged_df['SPECIAL_ALLOW'].astype('int64')

        # Import generated living table ([0] index for living file)
        special_df = pd.read_excel(org_file_path  +'/Special Allowance.xlsx')
        # Fetch standard special allowance values
        values = list(special_df['Allowance_Values'].values)
        # Fetch material Status
        positions = list(special_df['Position'].values)
        # Fetch Grade
        grades = list(special_df['Grade'].values)

        # df to store (concat) all results of auditing special files
        special_grade = pd.DataFrame()
        # Check grade and check the amount for the grade if correct
        for i in range(len(values)):
            # match the grade of merged df and allowance df together (note: if merged df didnt have grage then will never match with any grade)
            # special_grade_in_merged_df = merged_df[(merged_df['GRADE'].str.contains(grades[i], na=False, case=False, regex=False))][['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'GRADE','MARITAL_STATUS', 'SOCIAL_ALLOW']]

            # detect if SOCIAL_ALLOW in payroll not equal to the standard SOCIAL allowance (both values should equal otherwise will be detected) take material status into consideration
            detected_special_allowance = merged_df[(merged_df['SPECIAL_ALLOW'] != values[i]) & merged_df['POSITION_TITLE'].str.contains(positions[i], na=False, case=False, regex=True )  & merged_df['GRADE'].str.contains(grades[i], na=False,case=False,regex=True) ]
            # print(position)
            # fetch any values from master not match with values in living allowance
            if not detected_special_allowance.empty:
                # Append results in new df named living_grade
                special_grade = pd.concat([detected_special_allowance, special_grade])


        # special_grade= Organize_Data_View(special_grade)
        if not special_grade.empty:
            # Fetching the matched actual grades and values with the auditing summary results (living_grade df) that has non matched living allowance
            for i in range(len(values)):
                # match_special_grade = special_grade[special_grade['POSITION_TITLE'].str.contains(positions[i], na=False, case=False, regex=True)]
                special_grade.loc[special_grade['POSITION_TITLE'].str.contains(positions[i], na=False, case=False,regex=True), 'SPECIAL_AP_CSB'] = values[i]


            special_grade["SPECIAL_AP_CSB"] = special_grade["SPECIAL_AP_CSB"].astype(int)
        else:
            special_grade = pd.DataFrame(
                columns=[ 'CPR_NO', 'POSITION_TITLE','SPECIAL_ALLOW','SPECIAL_AP_CSB'])
    else:
        special_grade = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE','GRADE','SPECIAL_ALLOW','SPECIAL_AP_CSB'])

    # print(social_grade)
    return special_grade



def Check_Car_Allowance(df_master, df_payroll):
    """
    This function will be responsible to auditing Car Allowance.
    How the function work:
        1- filter required columns from master and payroll then merged both dfs by CPR_no
        2- check if there is any CAR allowance not follow the standard
    Notes: checking process depend on position_title for some employee and Judges Grade for Others

    Examples:
    __________
   UNDERSECRETARY  | PRESIDENT ==> should have allowance (300)
   J9 | J8 | J7  ==> should have allowance (300)


    Parameters
    ----------
    df_master
        employee master df to fetch the employee grade and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check Car allowance

    Returns
    -------
        Audit result for Car Allowance
    """

    # received master and payroll file
    # df_master = pd.read_excel('../NAO-Payroll/application/data/master_data/admin/Database_Jan_2021-_S-05092022_135309.xlsx')
    # df_payroll = pd.read_excel('../NAO-Payroll/application/data/MonthlyPayroll_data/admin/Feb-2022-payroll-05092022_135455.xlsx')


    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE','GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','CAR_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    org_file_path = organized_allowance_file()
    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

    if not merged_df.empty:
        # Dropping the missing LIVING_STD_ALLOW because it will shows in missing living_std table (no need to auditing them)
        # df= df.dropna(subset=['GRADE'])
        merged_df['CAR_ALLOW'] = merged_df['CAR_ALLOW'].fillna(0)
        #  convert LIVING_STD_ALLOW to int
        merged_df['CAR_ALLOW'] = merged_df['CAR_ALLOW'].astype('int64')

        # Import generated living table ([0] index for living file)
        car_df = pd.read_excel(org_file_path +'/Car Allowance.xlsx')
        # Fetch standard special allowance values
        values = list(car_df['Allowance_Values'].values)
        # Fetch Position
        positions = list(car_df['Position'].values)
        # Fetch Grade
        grades = list(car_df['Grade'].values)

        # df to store (concat) all results of auditing special files
        car_allow_position = pd.DataFrame()


        # Check grade and check the amount for the grade if correct
        for i in range(len(values)):
            # detect if CAR_ALLOW in payroll not equal to the standard CAR_ALLOW allowance based on position_title
            detected_car_allowance_position = merged_df[(merged_df['CAR_ALLOW'] != values[i]) & merged_df['POSITION_TITLE'].str.contains(positions[i], na=False, case=False, regex=True ) & merged_df['GRADE'].str.contains(grades[i], na=False,case=False,regex=True) ]

            print(detected_car_allowance_position)
            # print(position)
            # fetch any values from master not match with values in living allowance
            if not detected_car_allowance_position.empty:
                # Append results in new df named living_grade
                car_allow_position = pd.concat([detected_car_allowance_position, car_allow_position])

            # if not detected_car_allowance_grade.empty:
            #     # Append results in new df named living_grade
            #     car_allow_grade = pd.concat([detected_car_allowance_grade, car_allow_grade])



        if not car_allow_position.empty:
            # Fetching the matched actual grades and values with the auditing summary results (living_grade df) that has non matched living allowance
            for i in range(len(values)):
                # match_special_grade = special_grade[special_grade['POSITION_TITLE'].str.contains(positions[i], na=False, case=False, regex=True)]
                car_allow_position.loc[car_allow_position['POSITION_TITLE'].str.contains(positions[i], na=False, case=False,regex=True), 'CAR_ALLOW_AP_CSB'] = values[i]


            car_allow_position["CAR_ALLOW_AP_CSB"] = car_allow_position["CAR_ALLOW_AP_CSB"].astype(int)
            car_allow_position = car_allow_position[[ 'CPR_NO', 'POSITION_TITLE','GRADE','CAR_ALLOW','CAR_ALLOW_AP_CSB']]
            # make sure the fetch ASSISTANT are ASSISTANT UNDERSEC


        else:
            car_allow_position = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE','GRADE','CAR_ALLOW','CAR_ALLOW_AP_CSB'])


        # Fetch Other employees who are Not in high position and not in J grade that have 60 as car allowance & other df has same conditions but not equaal 60 and 0
        normal_employee_60,normal_employee_not60 = normalEmployeeCarAllow(merged_df)

    else:
        car_allow_position = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE','GRADE', 'CAR_ALLOW', 'CAR_ALLOW_AP_CSB'])
        # car_allow_grade = pd.DataFrame(columns=[ 'CPR_NO', 'GRADE', 'CAR_ALLOW', 'CAR_ALLOW_AP_CSB'])
        normal_employee_60 = pd.DataFrame(columns=[ 'CPR_NO', 'GRADE',  'POSITION_TITLE', 'CAR_ALLOW'])
        normal_employee_not60 = pd.DataFrame(columns=[ 'CPR_NO', 'GRADE', 'POSITION_TITLE', 'CAR_ALLOW'])

    # print(social_grade)
    return car_allow_position,normal_employee_60,normal_employee_not60


def normalEmployeeCarAllow(merged_df):
    """
    THIS FUNCTION to Fetch Other employees who are Not in high position and not in J grade that have 60 as car allowance and
    employees who are Not in high position and not in J grade that have other value than 60 or 0 as car allowance
    Parameters
    ----------
    merged_df
        merged df between payroll and master

    Returns
    -------
        data frame:
            1- employees who are Not in high position and not in J grade that have 60 as car allowance
            2- employees who are Not in high position and not in J grade that have other value than 60 or 0 as car allowance
    """
    # Fetch Other employees who are Not in high position that have 60 as car allowance (check db for high position)
    # merged_df['GradsApprev'] = merged_df['GRADE'].str.extract(r"([a-zA-Z][0-9]+)", expand=False)   # need then to use it in employee not having these grade (j1,j2,...j9)
    jgrades = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9']
    # read high ranking from database
    high_ranking_position_list = fetchAllPositionTitle()

    # Fetch Other employees who are Not in high position (FILTER 1)
    normal_employee = merged_df[(~(merged_df['POSITION_TITLE'].str.contains('|'.join(high_ranking_position_list), na=False, case=False,regex=True)))]
    # Filter normal employee results who are Not in GRADE J1 to J9 (FILTER 2)
    normal_employee = normal_employee[(~(normal_employee['GRADE'].str.contains('|'.join(jgrades), na=False, case=False, regex=True)))]
    # Fetch normal_employee who are have 60 as car allowance (FILTER 3.1)
    normal_employee_60 = normal_employee[normal_employee['CAR_ALLOW'] == 60]
    # Fetch normal_employee who are have car allowance other than 60 but not zero  (FILTER 3.2)
    normal_employee_not60 = normal_employee[(normal_employee['CAR_ALLOW'] != 60) & (normal_employee['CAR_ALLOW'] != 0)]

    return normal_employee_60,normal_employee_not60




def Check_Communication_Allowance(df_master,df_payroll):
    """
    THIS FUNCTION to Fetch employees who are having invalid communication allowance

    Examples:
    __________
   high ranking position  ==> should have allowance (50)
   Not high ranking position  ==> should have allowance (35|25)
   others ==> !=25 and != 35 and != 0  and != high position


    Parameters
    ----------
    df_master
        employee master df to fetch the employee info and concat the information with payroll via CPR Number
    df_payroll
        employee payroll df to check communication allowance

    Returns
    -------
        Audit result for communication Allowance
    """

    # filter df
    filtred_master_df = df_master[[ 'CPR_NO', 'POSITION_TITLE','GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    filtred_payroll_df = df_payroll[['CPR_NO','COMMUNICATION_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)


    org_file_path = organized_allowance_file()
    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    # remove spaces if any
    merged_df['POSITION_TITLE'] = merged_df['POSITION_TITLE'].str.strip()

    if not merged_df.empty:
        # read high ranking from database
        high_ranking_position_list = fetchAllPositionTitle()
        # read standard communication allowance form excel
        communication_allow_df = pd.read_excel(org_file_path +'/Communication Allowance.xlsx')
        communication_allow_df['Allowance_Values'] = communication_allow_df['Allowance_Values'].astype('int64')


        #___________ high ranking position  ==> should have allowance (50) _____
        # filter data to select only the employee with high position ranking
        emp_high_positions =  merged_df[((merged_df['POSITION_TITLE'].str.contains('|'.join(high_ranking_position_list), na=False, case=False, regex=True)))]

        # if employee with high positions not empty filter the one who are not take 50 as communication allowance else return empty df
        if not emp_high_positions.empty:
            #organized output
            # emp_high_positions = Organize_Data_View(emp_high_positions)
            communication_allow_df['Allowance_Values'] = communication_allow_df['Allowance_Values'].astype(str).astype(float)
            communication_allow_df['Allowance_Values']= communication_allow_df['Allowance_Values'].fillna(0.0)
            # fetch only who are not taking 50 as communication allowance
            emp_high_positions_comm_allow = emp_high_positions[(emp_high_positions['COMMUNICATION_ALLOW'] != communication_allow_df['Allowance_Values'][0]) & merged_df['GRADE'].str.contains(communication_allow_df['Grade'][0], na=False,case=False,regex=True)]
            emp_high_positions_comm_allow['ACTUAL_COMMUNICATION_ALLOW'] = communication_allow_df['Allowance_Values'][0]
            # print( communication_allow_df['Grade'][0] )
        else:
            emp_high_positions_comm_allow = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'COMMUNICATION_ALLOW','ACTUAL_COMMUNICATION_ALLOW','GRADE'])




        # ___________  Not high ranking position  ==> should have allowance (35|25) _____

        # filter data to select only the employee with not high position ranking
        emp_not_high_positions = merged_df[(~(merged_df['POSITION_TITLE'].str.contains('|'.join(high_ranking_position_list), na=False, case=False,regex=True)))]


        if not emp_not_high_positions.empty:
            # organized output
            emp_not_high_positions = Organize_Data_View(emp_not_high_positions)

            # fetch only who are taking 35 or 25 as communication allowance
            emp_not_high_positions_comm_allow = emp_not_high_positions[(emp_not_high_positions['COMMUNICATION_ALLOW'] == communication_allow_df['Allowance_Values'][1]) | (emp_not_high_positions['COMMUNICATION_ALLOW'] == communication_allow_df['Allowance_Values'][2])]


            # fetch only who are taking communication allowance not 25 ot 35 or 0
            emp_not_high_positions_invalid_comm_allow = emp_not_high_positions[(emp_not_high_positions['COMMUNICATION_ALLOW'] != communication_allow_df['Allowance_Values'][3])
                                                                                & (emp_not_high_positions['COMMUNICATION_ALLOW'] != communication_allow_df['Allowance_Values'][4])
                                                                                & (emp_not_high_positions['COMMUNICATION_ALLOW'] != communication_allow_df['Allowance_Values'][5])]


        else:
            emp_not_high_positions_comm_allow = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'COMMUNICATION_ALLOW','ACTUAL_COMMUNICATION_ALLOW'])
            emp_not_high_positions_invalid_comm_allow = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'COMMUNICATION_ALLOW','ACTUAL_COMMUNICATION_ALLOW'])



            #emp_high_positions_comm_allow.to_excel('emp_high_positions_comm_allow.xlsx')
            #merged_df.to_excel('merged_df.xlsx')

    else:
        emp_high_positions_comm_allow = pd.DataFrame(columns= ['CPR_NO', 'POSITION_TITLE','COMMUNICATION_ALLOW', 'ACTUAL_COMMUNICATION_ALLOW'])
        emp_not_high_positions_comm_allow = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'COMMUNICATION_ALLOW', 'ACTUAL_COMMUNICATION_ALLOW'])
        emp_not_high_positions_invalid_comm_allow = pd.DataFrame(columns=[ 'CPR_NO', 'POSITION_TITLE', 'COMMUNICATION_ALLOW', 'ACTUAL_COMMUNICATION_ALLOW'])


    return emp_high_positions_comm_allow,emp_not_high_positions_comm_allow, emp_not_high_positions_invalid_comm_allow


def Prepare_Employee_Allowance_report(master_df, payroll_file_path, file_name):
    """
    Excel Report of Employee Allowance Auditing Results
    This function responsible to prepare an excel file with dynamic sheet name if check box is checked (Employee Allowance Auditing Results)

    Parameters
    ----------
    master_df:
          Dataframe that has been selected by the end user to apply auditing process on employee information
    payroll_file_path:
        list contains the path for all selected payroll files

    file_name: the name used to generate meaningful name for the generated excel file (Employee_Deduction)
`
    Returns
    -------
    """
    gen_report_path= generate_report_path()
    filePath = gen_report_path + file_name + '_Auditing_Result_Report.xlsx'
    writer = pd.ExcelWriter(filePath, engine="xlsxwriter")
    # global result_df
    result_df = pd.DataFrame()
    for path in payroll_file_path:
        # result_df = pd.DataFrame()
        result_df.drop(result_df.index, inplace=True)
        # result_df.clear()
        sheetname, payroll_df = Import_Payroll_Data(path)
        # print(path)

        # Auditing Car & transport Allowance
        result_df = Check_Car_and_Transport(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'CarTransportAllowance'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing transport Allowance
        result_df = checkTransportAllowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'TransportAllowance'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)


        # Auditing noGradeWith Allowance
        result_df = noGradeWithAllowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'noGradeWithAllowance'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing no Material Status With Allowance
        result_df = noMaterialStatuseWithAllowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'noStatusWithAllowance'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)


        # Auditing Living Allowance
        result_df = Check_Living_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'LivingAllowance'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing Social Allowance
        result_df = Check_Social_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'SocialAllowance'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing Housing Allowance
        result_df = Check_Housing_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'HousingAllowance'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing Special Allowance
        result_df = Check_Special_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'SpecialAllowance'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing Car Allowance
        result_df,result_df3,result_df4 = Check_Car_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'CarAllowPosition'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)
        # if not result_df2.empty:
        #     merged_sheet_name = sheetname[0] + 'CarAllowBasedOnGrade'
        #     result_df2.to_excel(writer, sheet_name=merged_sheet_name, index=False)
        if not result_df3.empty:
            merged_sheet_name = sheetname[0] + 'CarAllowEarn60'
            result_df3.to_excel(writer, sheet_name=merged_sheet_name, index=False)
        if not result_df4.empty:
            merged_sheet_name = sheetname[0] + 'CarAllowNot60'
            result_df4.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        # Auditing Communication Allowance
        result_df, result_df2, result_df3 = Check_Communication_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'CommHighPosition'
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)
        if not result_df2.empty:
            merged_sheet_name = sheetname[0] + 'CommNormal'
            result_df2.to_excel(writer, sheet_name=merged_sheet_name, index=False)
        if not result_df3.empty:
            merged_sheet_name = sheetname[0] + 'InvalidCommAllow'
            result_df3.to_excel(writer, sheet_name=merged_sheet_name, index=False)


    writer.save()
