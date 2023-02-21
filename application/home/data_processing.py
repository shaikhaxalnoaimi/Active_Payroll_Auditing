import numpy as np
import pandas as pd
import openpyxl
import re
import datetime

from application import generate_report_path,generate_high_position_file_path,organized_allowance_file

pd.options.mode.chained_assignment = None
from application.Control_Panel.position_titles_db_Quires import fetchAllPositionTitle

"""
this function to remove unicode character from the column names (it should be multi-index) to avoid any mistake or un-known column 
:cvar recive readed excel as df 
:return: cleaned df with columns without any unicode character 
"""
def Unicode_Column_Names(df):

    if df.columns.nlevels > 1:
        #For two header
        col_list = []
        for tuple in df.columns:
            new_tuple = (
                re.sub(r"[\u3000\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f-\u202b]", "", tuple[0]),
                re.sub(r"[\u3000\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f-\u202b]", "", tuple[1])
            )
            col_list.append(new_tuple)


        df.columns = pd.MultiIndex.from_tuples(col_list)
    else:
        # For one header
        ''' Returns the column name without non ASCII characters'''
        string_unicodes = list(df.columns.values)
        i=0
        for string_unicode in string_unicodes:
            string_encode = string_unicode.encode("ascii", "ignore")
            string_decode = string_encode.decode()
            df.columns.values[i] = string_decode
            i = i +1

    return df


def fix_date(x):
    """
    Year 2000 (Y2K) issues: Python depends on the platform’s C library, which generally doesn’t have year 2000 issues,
    since all dates and times are represented internally as seconds since the epoch. Function strptime() can parse 2-digit years when given %y format code.
     When 2-digit years are parsed, they are converted according to the POSIX and ISO C standards:
     values 69–99 are mapped to 1969–1999, and values 0–68 are mapped to 2000–2068.
    Parameters
    ----------
    x: value of data of birth in df (new_file['DATE_OF_BIRTH'] )

    Returns
    -------
        fixing the wrong birth of data e.g. 2067-09-17 ==> 1967-09-17
    """
    if x.year > 1989:
        year = x.year - 100
    else:
        year = x.year
    return datetime.date(year, x.month, x.day)


def fix_date_leve2(x):
    """
    Year 2000 (Y2K) issues: Python depends on the platform’s C library, which generally doesn’t have year 2000 issues,
    since all dates and times are represented internally as seconds since the epoch. Function strptime() can parse 2-digit years when given %y format code.
     When 2-digit years are parsed, they are converted according to the POSIX and ISO C standards:
     values 69–99 are mapped to 1969–1999, and values 0–68 are mapped to 2000–2068.
    Parameters
    ----------
    x: value of data of birth in df (new_file['DATE_OF_BIRTH'] )

    Returns
    -------
        fixing the wrong birth of data e.g. 1925-09-17 ==> 1967-09-17
    """
    if (x.year <= 1923):
        year = x.year + 100
    else:
        year = x.year
    return datetime.date(year, x.month, x.day)



""":
Fetch the Employee Master Data
--------------------------------------------------------------------------------------------------------------------------------------
The below function responsible to fetch employee master data based on selected path
--------------------------------------------------------------------------------------------------------------------------------------
"""
"""_________________________ Import Master Data _________________"""
def Import_Master_Data(master_file_path):
    # master_file_path = 'C:/nao-payroll-deployment-dock/NAO-Payroll/application/data/master_data/admin/DatabaseCPR_test-06112022_090209.xlsx'
    xls = pd.ExcelFile(master_file_path)
    master_df = pd.read_excel(xls, xls.sheet_names[0])
    msheetname = xls.sheet_names[0]
    if not master_df.empty :
        master_df = Unicode_Column_Names(master_df)
        master_df['DATE_OF_BIRTH'] =  master_df['DATE_OF_BIRTH'] .apply(fix_date)
        master_df['DATE_OF_BIRTH'] = master_df['DATE_OF_BIRTH'].apply(fix_date_leve2)



    # master_df = pd.read_excel(master_file_path)
    # if not master_df.empty :
    #     master_df = Unicode_Column_Names(master_df)
    return master_df,msheetname

"""_________________________ Import Payroll Data _________________"""
def Import_Payroll_Data(payroll_file_path):
    # file_path = 'C:/NAO-Payroll/application/data/MonthlyPayroll_data/admin/Feb-2022-payroll-05092022_083548.xlsx'

    file = openpyxl.load_workbook(payroll_file_path)
    sheetname = file.sheetnames
    sheet_name = []
    for sheet in sheetname:
        sheet_name.append(sheet.replace(" ", ""))
    payroll_df = pd.read_excel(payroll_file_path)
    if not payroll_df.empty:
        payroll_df = Unicode_Column_Names(payroll_df)
    return sheet_name,payroll_df


######################################################################################-->
############# Show data in an approperiate way   ##################-->
######################################################################################-->
# Creating a function which will remove extra leading
# and tailing whitespace from the data.
# pass dataframe as a parameter here
def whitespace_remover(dataframe):
    # iterating over the columns
    for i in dataframe.columns:

        # checking datatype of each columns
        if dataframe[i].dtype == 'object':

            # applying strip function on column
            dataframe[i] = dataframe[i].map(str.strip)
        else:

            # if condn. is False then it will do nothing.
            pass




def Organize_Data_View(data):
    """
    This function to handle the data in order to show it in the an approperiates way to
    :cvar receive the data frame need to organized their data
    :return the organized columns  such as con vert cpr from float to integer
    """
    col = 'BASIC_SALARY'
    if col in data:
        data['BASIC_SALARY'] = data['BASIC_SALARY'].fillna(0.0)
        data['BASIC_SALARY'] = data['BASIC_SALARY'].astype(str).astype(float)



    col = "CPR_NO"
    if col in data:
        # data = whitespace_remover(data['CPR_NO'])
        data['CPR_NO']= data['CPR_NO'].replace(' ', '', regex=True)
        data['CPR_NO'] = data['CPR_NO'].replace('', '0', regex=True)
        data['CPR_NO'] = data['CPR_NO'].astype(str)
        # check if there is a - in cpr if yes remove it will all character comes after
        if data['CPR_NO'].str.contains('-').any():
            data['CPR_NO'] = data['CPR_NO'].str.split('-').str[0]
        # data['CPR_NO'].head(10)
        # to show cpr in an integer format not float
        # data= data.dropna(subset=['CPR_NO'])
        data['CPR_NO'] =  data['CPR_NO'].astype(str).astype(float)
        data['CPR_NO'] = data['CPR_NO'].fillna(0)
        data['CPR_NO'] = data['CPR_NO'].astype(float).astype('int64')


    col = "MARITAL_STATUS"
    if col in data:
        # remove spaces if any
        data['MARITAL_STATUS'] = data['MARITAL_STATUS'].str.strip()
        # replace null with   space
        data['MARITAL_STATUS']= data['MARITAL_STATUS'].replace(' ', '', regex=True)
        #replace space with _
        data['MARITAL_STATUS'] = data['MARITAL_STATUS'].replace('', '_', regex=True)


    col = "DIRECTORATE"
    if col in data:
        if isinstance(data['DIRECTORATE'], str):
            data['DIRECTORATE'] = data['DIRECTORATE'].fillna('_')
        else:
            data['DIRECTORATE'] = data['DIRECTORATE'].fillna('_')
            data['DIRECTORATE'] = data['DIRECTORATE'].astype(str)

        # replace null with   space
        data['DIRECTORATE']= data['DIRECTORATE'].replace(' ', '', regex=True)
        #replace space with
        data['DIRECTORATE'] = data['DIRECTORATE'].replace('', '_', regex=True)

        # remove spaces if any
        data['DIRECTORATE'] = data['DIRECTORATE'].str.strip()

    col = "CATEGORY"
    if col in data:
        data['DIRECTORATE'] = data['DIRECTORATE'].astype(str)
        # replace null with   space
        data['CATEGORY']= data['CATEGORY'].replace(' ', '', regex=True)
        #replace space with _
        data['CATEGORY'] = data['CATEGORY'].replace('', '_', regex=True)
        data['CATEGORY'] = data['CATEGORY'].fillna('_')
        # remove spaces if any
        data['CATEGORY'] = data['CATEGORY'].str.strip()

    col = "EMPLOYEE_NAME"
    if col in data:
        # to show null name with empty cell instad of nan
        data['EMPLOYEE_NAME'] = data['EMPLOYEE_NAME'].fillna("-")
    col = "POSITION_TITLE"
    if col in data:
        data['POSITION_TITLE'] = data['POSITION_TITLE'].str.strip()
        data['POSITION_TITLE'] = data['POSITION_TITLE'].fillna("_")
    col = "ACCOUNTNO"
    if col in data:
        # data = whitespace_remover(data['CPR_NO'])
        data['ACCOUNTNO'] = data['ACCOUNTNO'].astype(str)
        data['ACCOUNTNO'] = data['ACCOUNTNO'].replace(' ', '', regex=True)
        data['ACCOUNTNO'] = data['ACCOUNTNO'].replace('', '0', regex=True)

        # check if there is a - in cpr if yes remove it will all character comes after
        if data['ACCOUNTNO'].str.contains('-').any():
            data['ACCOUNTNO'] = data['ACCOUNTNO'].replace('-', '0', regex=True)
        # data['CPR_NO'].head(10)
        # to show cpr in an integer format not float
        # data= data.dropna(subset=['CPR_NO'])
        data['ACCOUNTNO'] = data['ACCOUNTNO'].astype(str).astype(float)
        data['ACCOUNTNO'] = data['ACCOUNTNO'].fillna(0)
        data['ACCOUNTNO'] = data['ACCOUNTNO'].astype(float).astype('int64')


    col = "AGE"
    if col in data:
        # to show age in an integer format not float
        data['AGE'] = data['AGE'].fillna(0)
        data['AGE'] = data['AGE'].astype('int64')

    col = "DATE_OF_BIRTH"
    if col in data:
        # to show DATE TIME in an DATE format
        data['DATE_OF_BIRTH'] = pd.to_datetime(data['DATE_OF_BIRTH']).dt.date

    col = "ANNUAL"
    if col in data:
        data['ANNUAL'] = data['ANNUAL'].replace(' ', '', regex=True)
        data['ANNUAL'] = data['ANNUAL'].replace('', '0', regex=True)
        data['ANNUAL'] = data['ANNUAL'].astype(str).astype(float)
        data['ANNUAL'] = data['ANNUAL'].fillna(0.0)
        # data['ANNUAL'] = data['ANNUAL'].astype(float).astype('int64')
        # # to show age in an integer format not float
        # data['ANNUAL'] = data['ANNUAL'].fillna(0)
        # data['ANNUAL'] = data['ANNUAL'].astype('int64')

    col = "SICK"
    if col in data:
        data['SICK'] = data['SICK'].replace(' ', '', regex=True)
        data['SICK'] = data['SICK'].replace('', '0', regex=True)
        data['SICK'] = data['SICK'].astype(str).astype(float)
        data['SICK'] = data['SICK'].fillna(0.0)



    col = "CAR"
    if col in data:
        # to show car allowance in an integer format not float
        data['CAR'] = data['CAR'].replace(' ', '', regex=True)
        data['CAR'] = data['CAR'].replace('', '0', regex=True)
        data['CAR'] = data['CAR'].astype(str).astype(float)
        data['CAR'] = data['CAR'].fillna(0.0)
        # data['CAR'] = data['CAR'].astype('int64')

        # data['CAR'] = data['CAR'].fillna(0)
        # data['CAR'] = data['CAR'].astype('int64')

    col = "TRANSPORT"
    if col in data:
        data['TRANSPORT'] = data['TRANSPORT'].replace(' ', '', regex=True)
        data['TRANSPORT'] = data['TRANSPORT'].replace('', '0', regex=True)
        data['TRANSPORT'] = data['TRANSPORT'].astype(str).astype(float)
        data['TRANSPORT'] = data['TRANSPORT'].fillna(0.0)


    col = "SPECIAL_ALLOW"
    if col in data:
        # data['SPECIAL_ALLOW'] = data['SPECIAL_ALLOW'].replace(' ', '', regex=True)
        # data['SPECIAL_ALLOW'] = data['SPECIAL_ALLOW'].replace('', '0', regex=True)

        data['SPECIAL_ALLOW'] = data['SPECIAL_ALLOW'].fillna(0.0)
        data['SPECIAL_ALLOW'] = data['SPECIAL_ALLOW'].astype(str).astype(float)


        # data['SPECIAL'] = data['SPECIAL'].fillna(0.0)

    col = "PFC"
    if col in data:
        data['PFC'] = data['PFC'].replace(' ', '', regex=True)
        data['PFC'] = data['PFC'].replace('', '0', regex=True)
        data['PFC'] = data['PFC'].astype(str).astype(float)
        data['PFC'] = data['PFC'].fillna(0.0)

        # data['PFC'] = data['PFC'].fillna(0.0)

    col = "SOCIAL_PFC"
    if col in data:
        data['SOCIAL_PFC'] = data['SOCIAL_PFC'].replace(' ', '', regex=True)
        data['SOCIAL_PFC'] = data['SOCIAL_PFC'].replace('', '0', regex=True)
        data['SOCIAL_PFC'] = data['SOCIAL_PFC'].astype(str).astype(float)
        data['SOCIAL_PFC'] = data['SOCIAL_PFC'].fillna(0.0)


        # data['SOCIAL_PFC'] = data['SOCIAL_PFC'].fillna(0.0)
    col = 'UNEMPLOYMENT_INSUR_DED'
    if col in data:
        data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].replace(' ', '', regex=True)
        data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].replace('', '0', regex=True)
        data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].astype(str).astype(float)
        data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].fillna(0.0)
        #
        # data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].fillna(0.0)
        # data['UNEMPLOYMENT_INSUR_DED'] = data['UNEMPLOYMENT_INSUR_DED'].astype('float')

    col = 'SOCIAL_PEN_FUND_CONTRIP_DED'
    if col in data:
        data['SOCIAL_PEN_FUND_CONTRIP_DED'] = data['SOCIAL_PEN_FUND_CONTRIP_DED'].replace(' ', '', regex=True)
        data['SOCIAL_PEN_FUND_CONTRIP_DED'] = data['SOCIAL_PEN_FUND_CONTRIP_DED'].replace('', '0', regex=True)
        data['SOCIAL_PEN_FUND_CONTRIP_DED'] = data['SOCIAL_PEN_FUND_CONTRIP_DED'].astype(str).astype(float)
        data['SOCIAL_PEN_FUND_CONTRIP_DED'] = data['SOCIAL_PEN_FUND_CONTRIP_DED'].fillna(0.0)

    col = 'PENSION_FUND_CONTRIPUTION_DED'
    if col in data:
        data['PENSION_FUND_CONTRIPUTION_DED'] = data['PENSION_FUND_CONTRIPUTION_DED'].replace(' ', '', regex=True)
        data['PENSION_FUND_CONTRIPUTION_DED'] = data['PENSION_FUND_CONTRIPUTION_DED'].replace('', '0', regex=True)
        data['PENSION_FUND_CONTRIPUTION_DED'] = data['PENSION_FUND_CONTRIPUTION_DED'].astype(str).astype(float)
        data['PENSION_FUND_CONTRIPUTION_DED'] = data['PENSION_FUND_CONTRIPUTION_DED'].fillna(0.0)

    col = "SOCIAL_ALLOW"
    if col in data:

        data['SOCIAL_ALLOW'] = data['SOCIAL_ALLOW'].fillna(0.0)
        data['SOCIAL_ALLOW'] = data['SOCIAL_ALLOW'].astype(str).astype(float)


    col = 'COMMUNICATION_ALLOW'
    if col in data:
        data['COMMUNICATION_ALLOW'] = data['COMMUNICATION_ALLOW'].replace(' ', '', regex=True)
        data['COMMUNICATION_ALLOW'] = data['COMMUNICATION_ALLOW'].replace('', '0', regex=True)
        data['COMMUNICATION_ALLOW'] = data['COMMUNICATION_ALLOW'].astype(str).astype(float)
        data['COMMUNICATION_ALLOW'] = data['COMMUNICATION_ALLOW'].fillna(0.0)


    col = 'LIVING_STD_ALLOW'
    if col in data:
        data['LIVING_STD_ALLOW'] = data['LIVING_STD_ALLOW'].replace(' ', '', regex=True)
        data['LIVING_STD_ALLOW'] = data['LIVING_STD_ALLOW'].replace('', '0', regex=True)
        data['LIVING_STD_ALLOW'] = data['LIVING_STD_ALLOW'].astype(str).astype(float)
        data['LIVING_STD_ALLOW'] = data['LIVING_STD_ALLOW'].fillna(0)
        data['LIVING_STD_ALLOW'] = data['LIVING_STD_ALLOW'].astype(int)

    col = 'HOUSING_ALLOW'
    if col in data:
        data['HOUSING_ALLOW'] = data['HOUSING_ALLOW'].replace(' ', '', regex=True)
        data['HOUSING_ALLOW'] = data['HOUSING_ALLOW'].replace('', '0', regex=True)
        data['HOUSING_ALLOW'] = data['HOUSING_ALLOW'].astype(str).astype(float)
        data['HOUSING_ALLOW'] = data['HOUSING_ALLOW'].fillna(0)
        data['HOUSING_ALLOW'] = data['HOUSING_ALLOW'].astype(int)

    col = 'STANDARD'
    if col in data:
        data['STANDARD'] = data['STANDARD'].replace(' ', '', regex=True)
        data['STANDARD'] = data['STANDARD'].replace('', '0', regex=True)
        data['STANDARD'] = data['STANDARD'].astype(str).astype(float)
        data['STANDARD'] = data['STANDARD'].fillna(0.0)


    col = 'TRANSPORT_ALLOW'
    if col in data:
        data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].replace(' ', '', regex=True)
        data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].replace('', '0', regex=True)
        data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].astype(str).astype(float)
        data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].fillna(0.0)
        #
        # data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].fillna(0)
        # data['TRANSPORT_ALLOW'] = data['TRANSPORT_ALLOW'].astype('int64')
    col  = 'CAR_ALLOW'
    if col in data:
        data['CAR_ALLOW'] = data['CAR_ALLOW'].replace(' ', '', regex=True)
        data['CAR_ALLOW'] = data['CAR_ALLOW'].replace('', '0', regex=True)
        data['CAR_ALLOW'] = data['CAR_ALLOW'].astype(str).astype(float)
        data['CAR_ALLOW'] = data['CAR_ALLOW'].fillna(0.0)
        #
        # data['CAR_ALLOW'] = data['CAR_ALLOW'].fillna(0)
        # data['CAR_ALLOW'] = data['CAR_ALLOW'].astype('int64')

    col= 'UNEMP_DEDUCTION'
    if col in data:
        data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].replace(' ', '', regex=True)
        data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].replace('', '0', regex=True)
        data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].astype(str).astype(float)
        data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].fillna(0.0)

        # data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].fillna(0)
        # data['UNEMP_DEDUCTION'] = data['UNEMP_DEDUCTION'].astype('float')

    col = 'REGULAR_OVERTIME'
    if col in data:
        data['REGULAR_OVERTIME'] = data['REGULAR_OVERTIME'].replace(' ', '', regex=True)
        data['REGULAR_OVERTIME'] = data['REGULAR_OVERTIME'].replace('', '0', regex=True)
        data['REGULAR_OVERTIME'] = data['REGULAR_OVERTIME'].astype(str).astype(float)
        data['REGULAR_OVERTIME'] = data['REGULAR_OVERTIME'].fillna(0.0)

        # data["REGULAR_OVERTIME"] = data["REGULAR_OVERTIME"].fillna(0)

    col = 'HOLIDAY_OVERTIME'
    if col in data:
        data['HOLIDAY_OVERTIME'] = data['HOLIDAY_OVERTIME'].replace(' ', '', regex=True)
        data['HOLIDAY_OVERTIME'] = data['HOLIDAY_OVERTIME'].replace('', '0', regex=True)
        data['HOLIDAY_OVERTIME'] = data['HOLIDAY_OVERTIME'].astype(str).astype(float)
        data['HOLIDAY_OVERTIME'] = data['HOLIDAY_OVERTIME'].fillna(0.0)

        # data["HOLIDAY_OVERTIME"] = data["HOLIDAY_OVERTIME"].fillna(0)

    col = 'HOLIDAY_OT_HOURS'
    if col in data:
        data['HOLIDAY_OT_HOURS'] = data['HOLIDAY_OT_HOURS'].replace(' ', '', regex=True)
        data['HOLIDAY_OT_HOURS'] = data['HOLIDAY_OT_HOURS'].replace('', '0', regex=True)
        data['HOLIDAY_OT_HOURS'] = data['HOLIDAY_OT_HOURS'].astype(str).astype(float)
        data['HOLIDAY_OT_HOURS'] = data['HOLIDAY_OT_HOURS'].fillna(0.0)

        # data["HOLIDAY_OT_HOURS"] = data["HOLIDAY_OT_HOURS"].fillna(0)
        # data['HOLIDAY_OT_HOURS'] = data['HOLIDAY_OT_HOURS'].astype('int64')

    col = 'REGULAR_OT_HOURS'
    if col in data:
        data['REGULAR_OT_HOURS'] = data['REGULAR_OT_HOURS'].replace(' ', '', regex=True)
        data['REGULAR_OT_HOURS'] = data['REGULAR_OT_HOURS'].replace('', '0', regex=True)
        data['REGULAR_OT_HOURS'] = data['REGULAR_OT_HOURS'].astype(str).astype(float)
        data['REGULAR_OT_HOURS'] = data['REGULAR_OT_HOURS'].fillna(0.0)
    col = 'GRADE'
    if col in data:
        #convert to upper
        data['GRADE'] = data['GRADE'].str.upper()
        # remove spaces if any
        data['GRADE'] = data['GRADE'].str.strip()
        # data['GRADE'] = data['GRADE'].astype(str)
        # fill null
        data['GRADE'] = data['GRADE'].fillna("_")

    col = "NATIONALITY"
    if col in data:
        #convert to upper
        data['NATIONALITY'] = data['NATIONALITY'].str.upper()
        # remove spaces if any
        data['NATIONALITY'] = data['NATIONALITY'].str.strip()
        # fill null
        data['NATIONALITY'] = data['NATIONALITY'].fillna("_")




        # data["REGULAR_OT_HOURS"] = data["REGULAR_OT_HOURS"].fillna(0)
        # data['REGULAR_OT_HOURS'] = data['REGULAR_OT_HOURS'].astype('int64')



    return data

""":
Employee Information Auditing Process 
--------------------------------------------------------------------------------------------------------------------------------------
The below functions responsible to handle all employee information auditing and return the table results for each auditing process 
--------------------------------------------------------------------------------------------------------------------------------------
"""
#_________________________ Check_Duplicate_Name_________________
def Check_Duplicate_Name(df):
    # Duplicate Name
    duplicate_in_EmployeeName = df.duplicated(subset=['EMPLOYEE_NAME'], keep=False)
    DuplicateName = df.loc[duplicate_in_EmployeeName][['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE']]

    #Drop null name because if null duplicated doesnt means it is duplicate name
    DuplicateName = DuplicateName.dropna(subset=['EMPLOYEE_NAME'])

    #to show data in organized way
    DuplicateName = Organize_Data_View(DuplicateName)



    return DuplicateName


#_________________________ Check_Missing_Name_________________
def Check_Missing_Name(df):
    missing_name = df[(df['EMPLOYEE_NAME'].isnull()) | (df['EMPLOYEE_NAME'].isna())][['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE']]

    # to show data in organized way
    missing_name = Organize_Data_View(missing_name)

    return missing_name

#_________________________ Check_Invalid_CPR_________________
def Check_Invalid_CPR(master_df):
    # df,msheetname = Import_Master_Data('C:/nao-payroll-deployment-dock/NAO-Payroll/application/data/master_data/admin/DatabaseCPR_test-06112022_090209.xlsx')

    master_df = Organize_Data_View(master_df)

    # convert date to datetime type
    master_df['DATE_OF_BIRTH'] = pd.to_datetime(master_df['DATE_OF_BIRTH'], errors='coerce')
    # drop any value == 2122-02-22 because these were empty but we fill it by default value
    master_df = master_df.drop(master_df[master_df.DATE_OF_BIRTH == '2122-02-22'].index)
    # extract year from the date of birth
    master_df['year'] = pd.DatetimeIndex(master_df['DATE_OF_BIRTH']).year
    # convert the year to integer
    master_df['year'] = master_df['year'].astype(str).astype(float)
    master_df['year'] = master_df['year'].astype(float).astype('int64')
    # count length of the cpr number
    master_df['CPRCount'] = master_df['CPR_NO'].astype(str).map(len)
    # filter only the one that dont equal 9
    InvalidCPR = master_df[(master_df['CPRCount'] != 9)]
    # if length equal 6 make sure these cpr not born in 2000
    InvalidCPR = InvalidCPR[~((InvalidCPR['CPRCount'] == 6) & (InvalidCPR['year'] == 2000)) ]
    InvalidCPR = InvalidCPR[~((InvalidCPR['CPRCount'] == 7) & (InvalidCPR['year'].between(2001, 2009))) ]
    InvalidCPR = InvalidCPR[~((InvalidCPR['CPRCount'] == 8) & (InvalidCPR['year'] >= 2010))]


    InvalidCPR = InvalidCPR[['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE','DATE_OF_BIRTH','year']]

    return InvalidCPR

#_________________________ Check_Duplicate_CPR_________________
def Check_Duplicate_CPR(df):
    duplicate_in_EmployeeCPR = df.duplicated(subset=['CPR_NO'], keep=False)
    DuplicateCPR = df.loc[duplicate_in_EmployeeCPR][['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE']]

    # Drop null cpr becuase if null duplicated doesnt means it is duplicate cpr
    DuplicateCPR = DuplicateCPR.dropna(subset=['CPR_NO'])

    # to show data in organized way
    DuplicateCPR = Organize_Data_View(DuplicateCPR)

    return DuplicateCPR


#_________________________ Check_Duplicate_account_Number_________________
def Check_Duplicate_Accont_No(df):
    duplicate_in_AcountNo = df.duplicated(subset=['ACCOUNTNO'], keep=False)
    DuplicateAccNo= df.loc[duplicate_in_AcountNo][[ 'EMPLOYEE_NAME', 'CPR_NO','POSITION_TITLE', 'ACCOUNTNO']]

    # Drop null ACCOUNTNO becuase if null duplicated doesnt means it is duplicate ACCOUNTNO
    DuplicateAccNo = DuplicateAccNo.dropna(subset=['ACCOUNTNO'])

    # to show data in organized way
    DuplicateAccNo = Organize_Data_View(DuplicateAccNo)
    return DuplicateAccNo

#_________________________ Check_Invalid_Account_No_________________
def Check_Invalid_Account_No(df):
    ZeroEmpty_in_EmployeeAccountNum = df[(df['ACCOUNTNO'].isnull()) | (df['ACCOUNTNO'].isna()) | (df['ACCOUNTNO'] == 0)]
    ZeroEmpty_in_EmployeeAccountNum = ZeroEmpty_in_EmployeeAccountNum[['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'ACCOUNTNO']]

    # to show data in organized way
    ZeroEmpty_in_EmployeeAccountNum = Organize_Data_View(ZeroEmpty_in_EmployeeAccountNum)

    return ZeroEmpty_in_EmployeeAccountNum

#_________________________ Check_Age_________________
def Check_Age(df):
    # to show data in organized way
    df = Organize_Data_View(df)
    df1 = df
    df1['DATE_OF_BIRTH1'] = df1['DATE_OF_BIRTH']
    df1['DATE_OF_BIRTH1'] = pd.to_datetime(df1['DATE_OF_BIRTH1'], errors='coerce')

    df1 = df1.drop(df1[df1.DATE_OF_BIRTH1 == '2122-02-22'].index)

    now = pd.to_datetime('now', utc=True)

    df2 = df1
    df2['AGE'] = (now.year - df1['DATE_OF_BIRTH1'].dt.year) - ((now.month - df1['DATE_OF_BIRTH1'].dt.month) < 0)

    df3 = df2[(df2['AGE'] < 0)]

    df3.loc[:, 'AGE'] = df3['AGE'] + 100
    df3

    df4 = df2[(df2['AGE'] > 0)]
    df4

    frames = [df3, df4]

    df5 = pd.concat(frames)

    invalidAge = df5[((df5['AGE'] <= 17) | (df5['AGE'] >= 65))]

    final_results = invalidAge[(invalidAge['CATEGORY'].str.contains('Permanent|Re-Employed', na=False, case=False, regex=True))]

    final_results = final_results[['CPR_NO', 'DATE_OF_BIRTH', 'AGE','CATEGORY']]

    return final_results

#_________________________ Employee with no Categories _________________
def Check_Categories(df):
    # print(df['DATE_OF_BIRTH'])
    """

    Parameters
    ----------
    df

    Returns
    -------
    all employee who do no have category
    """
    # to show data in organized way
    df = Organize_Data_View(df)
    final_results = df[(df['CATEGORY']=='_')]
    final_results['DATE_OF_BIRTH'] = final_results['DATE_OF_BIRTH'].astype(str)
    # any date with 2122-02-22 this mean it was empty and fill with this value so need to represented to the end user as _ (missing date)
    final_results.loc[final_results['DATE_OF_BIRTH'] == '2122-02-22', 'DATE_OF_BIRTH'] = '_'
    final_results = final_results[['CPR_NO', 'POSITION_TITLE', 'DATE_OF_BIRTH', 'CATEGORY']]
    return final_results

#_________________________ Check_Annual_Leave_________________
def Check_Annual_leave(df,sheetname):
    split = sheetname.split("-")
    month, name = split
    month = month.upper()
    if month == 'JAN':
        df = Organize_Data_View(df)
        HighAnnual = df[(df['ANNUAL'] > 77.5)]
        HighAnnual = HighAnnual[['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'ANNUAL']]
    else:
        HighAnnual = pd.DataFrame(columns = ['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'ANNUAL'])

    return HighAnnual


#_________________________ Check_Sick_Leave_________________
def Check_Sick_leave(df,sheetname):
    split = sheetname.split("-")
    month, name = split
    month = month.upper()
    if month == 'JAN':
        df = Organize_Data_View(df)
        HighSickLeave = df[(df['SICK'] > 242.5)]
        HighSickLeave = HighSickLeave[['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'SICK']]
    else:
        HighSickLeave = pd.DataFrame(columns=['EMPLOYEE_NAME', 'CPR_NO', 'POSITION_TITLE', 'SICK'])

    return HighSickLeave


"""
This function to check if there is two high ranking position (job title) at the same organization
:param df: receive the employee master database as data frame
:return: employee records if there is two same high ranking position at the same organization
"""
def Check_High_Rank_Posisiton(df):
    # high_ranking_position_list = ["CEO", "Undersecretary", "Deputy CEO", "Assistant undersecretary", "Director"]
    # 870301080, 870406469, 620053291,630231605 give them duplicate grade to test
    df = Organize_Data_View(df)
    #read high ranking from database
    high_ranking_position_list = fetchAllPositionTitle()
    # fetch all employee if high ranking from master match with the db
    check_rank = df[(df['POSITION_TITLE'].str.match('|'.join(high_ranking_position_list), na=False, case=False))]
    duplicateHighRanking = check_rank.duplicated(subset=['POSITION_TITLE', 'DIRECTORATE'], keep=False)
    duplicate_high_ranking = check_rank.loc[duplicateHighRanking][['CPR_NO', 'POSITION_TITLE', 'DIRECTORATE', 'GRADE']]
    # Generate high position rules file path
    file_path = generate_high_position_file_path()
    # the acceptance grade from E4 TO E7
    accepted_grade = pd.read_excel(file_path + '/AcceptanceGrade.xlsx')
    accepted_grade = accepted_grade.Grade.values.tolist()
    # Check grade of duplicated positions
    final_results = pd.DataFrame(columns= ['CPR_NO', 'POSITION_TITLE','DIRECTORATE','GRADE'])

    for i in range(len(accepted_grade)):
        duplicate = duplicate_high_ranking[(duplicate_high_ranking['GRADE'].str.contains(accepted_grade[i], na=False, case=False, regex=False))]
        final_results = pd.concat([duplicate,final_results])

    return final_results




def Missing_GRADE(df_master):
    """
    function to fetch missing GRADE
    Parameters
    ----------
    df
        receive employee master df to check missing 'GRADE'

    Returns
    -------
    missing_grade
        results of missing 'GRADE'
    """
    df_master = Organize_Data_View(df_master)
    df_master = df_master[['CPR_NO','POSITION_TITLE','GRADE']]
    # Import standard grade path
    org_file_path = organized_allowance_file()
    # read standard grade file
    standard_grade_df = pd.read_excel(org_file_path + '/Standard Grade.xlsx')

    # join the lise valu using | character
    join_grade= '|'.join(standard_grade_df['Grade'].tolist())

    missing_grade = df_master[~(df_master['GRADE'].str.contains(join_grade, na=False, case=False, regex=True))][['CPR_NO', 'POSITION_TITLE', 'GRADE']]
    # missing_grade = unknown_grade[unknown_grade['GRADE'] != 'N']

    return missing_grade


def Missing_MARITAL_STATUS(df_master):
    """
    function to fetch missing MARITAL_STATUS
    Parameters
    ----------
    df
        receive employee master df to check missing 'MARITAL_STATUS'
    Returns
    -------
    missing_material_status
        results of missing 'MARITAL_STATUS'
    """
    # import pandas as pd
    # df_master = pd.read_excel(
    #     'C:/nao-payroll-deployment-dock/NAO-Payroll/application/data/master_data/admin/Master_as_of_July-_with_error-04102022_102708.xlsx')

    # df_master = pd.read_excel('C:/NAO-Payroll/application/data/master_data/admin/Database_Jan_2021-_S-10092022_171202.xlsx')
    # fill null and convert 'LIVING_STD' from float to int
    df_master = Organize_Data_View(df_master)
    # get the missing data of LIVING_STD
    missing_material_status= df_master[df_master['MARITAL_STATUS'] == "_"][['CPR_NO','POSITION_TITLE','MARITAL_STATUS']]


    return missing_material_status


def Missing_Employee(master_df,payroll_df):
    """

    Parameters
    ----------
    master_df the selected master data frame
    payroll_df the selected payroll data frame (allow only one payroll)

    Returns
    -------
    the employee who are in master but not in payroll df

    """
    master_df = Organize_Data_View(master_df)
    payroll_df = Organize_Data_View(payroll_df)
    # missing_in_master = master_df[~master_df.isin(payroll_df)].dropna()
    common1 = master_df.merge(payroll_df, on=['CPR_NO'])
    # fetch all employees that are in master but not in employee
    missing_in_master = master_df[(~master_df.CPR_NO.isin(common1.CPR_NO)) & (~master_df.CPR_NO.isin(common1.CPR_NO))]
    missing_in_master =  missing_in_master[['CPR_NO','EMPLOYEE_NAME','POSITION_TITLE','GRADE']]

    common2 = payroll_df.merge(master_df, on=['CPR_NO'])
    # fetch all employees that are in payroll but not in master
    missing_in_payroll = payroll_df[(~payroll_df.CPR_NO.isin(common2.CPR_NO)) & (~payroll_df.CPR_NO.isin(common2.CPR_NO))]
    missing_in_payroll= missing_in_payroll[['CPR_NO']]

    return missing_in_master,missing_in_payroll

""":
Deduction Auditing Process 
--------------------------------------------------------------------------------------------------------------------------------------
The below functions responsible to handle all employee deduction Process and return the table results for each auditing process 
--------------------------------------------------------------------------------------------------------------------------------------
"""



"""
This function to calculate and check Pension Allowance deduction if -------------
:param df: receive the employee master database as data frame
:return: employee records if there is an invalid Pension_Allowance
"""
def Check_Pension_Allowance(df_master,df_payroll):
    # df_master[['BASIC_SALARY', 'SOCIAL', 'SPECIAL']] = df_master[['BASIC_SALARY', 'SOCIAL', 'SPECIAL']].fillna(0)


    filtred_master_df =df_master[['CPR_NO', 'EMPLOYEE_NAME',  'POSITION_TITLE',  'NATIONALITY']]
    filtred_master_df = Organize_Data_View(filtred_master_df)


    # df_payroll = pd.read_excel('C:/NAO-Payroll/application/data/MonthlyPayroll_data/admin/Feb-2022-payroll-05092022_083548.xlsx')
    filtred_payroll_df = df_payroll[['CPR_NO','PENSION_FUND_CONTRIPUTION_DED','SPECIAL_ALLOW','BASIC_SALARY']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    # Check Pension Fund Deduction
    col_sum = (filtred_payroll_df['BASIC_SALARY'] + filtred_payroll_df['SPECIAL_ALLOW']) * 0.06
    filtred_payroll_df["CALCULATED_PNE_DEDC"] = col_sum

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    merged_df['CALCULATED_PNE_DEDC'] =  merged_df['CALCULATED_PNE_DEDC'].fillna(0.0)

    merged_df['CHECK_PENSION'] = merged_df['PENSION_FUND_CONTRIPUTION_DED'].astype(float).astype('int64') - merged_df['CALCULATED_PNE_DEDC'].astype(float).astype('int64')
    # merged_df= merged_df.round({'CHECK_PENSION': 3})
    merged_df['CHECK_PENSION'] = np.trunc(1000 *   merged_df['CHECK_PENSION'] ) / 1000

    merged_df['PERCENTAGE'] = merged_df['PENSION_FUND_CONTRIPUTION_DED']/ (merged_df['BASIC_SALARY'] + merged_df['SPECIAL_ALLOW'])
    merged_df['PERCENTAGE'] = round(merged_df['PERCENTAGE'], 2)
    merged_df['PERCENTAGE'] = merged_df['PERCENTAGE'] * 100
    # merged_df= merged_df.round({'PENSION_DEDUCTION': 3})
    merged_df['CALCULATED_PNE_DEDC'] =np.trunc(1000 *   merged_df['CALCULATED_PNE_DEDC'] ) / 1000
    merged_df['PERCENTAGE'] = np.trunc(1000 *   merged_df['PERCENTAGE'] ) / 1000

    # merged_df['PERCENTAGE'] = merged_df['PERCENTAGE'].round(decimals=4)
    # merged_df= merged_df.round({'PERCENTAGE', })

    check_pension_fund = merged_df[(merged_df['NATIONALITY'].str.contains('BAHRAINI', na=False, case=False, regex=False))]
    check_pension_fund = check_pension_fund[check_pension_fund['PERCENTAGE'] !=6]
    check_pension_fund = check_pension_fund[['CPR_NO','BASIC_SALARY', 'SPECIAL_ALLOW', 'PERCENTAGE', 'CALCULATED_PNE_DEDC','PENSION_FUND_CONTRIPUTION_DED']]
    check_pension_fund.rename(columns=lambda x: x.replace('CALCULATED_PNE_DEDC', 'CALCULATED'), inplace=True)
    check_pension_fund.rename(columns=lambda x: x.replace('PENSION_FUND_CONTRIPUTION_DED', 'ACTUAL'), inplace=True)
    return check_pension_fund


"""
This function to calculate and Social_Allowance_Deduction  -------------
:param df: receive the employee master database as data frame
:return: employee records if there is an invalid Social_Allowance_Deduction
"""
def Check_Social_Allowance_Deduction(df_master,df_payroll):
    # Drop null Social, and SOCIAL_PFC because if null means the calculation not fair

    filtred_master_df = df_master[['CPR_NO', 'NATIONALITY']]
    filtred_master_df = Organize_Data_View(filtred_master_df)

    # df_master[['BASIC_SALARY', 'SOCIAL', 'SPECIAL']] = df_master[['BASIC_SALARY', 'SOCIAL', 'SPECIAL']].fillna(0)


    # df_payroll = pd.read_excel('C:/NAO-Payroll/application/data/MonthlyPayroll_data/admin/payroll-30082022_094926.xlsx')
    filtred_payroll_df = df_payroll[['CPR_NO', 'SOCIAL_PEN_FUND_CONTRIP_DED', 'BASIC_SALARY', 'SOCIAL_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    # Check Pension Fund Deduction
    col_sum = (filtred_payroll_df['SOCIAL_ALLOW']) * 0.06
    filtred_payroll_df['CALCULATED_SOCIAL_DEDUC'] = col_sum
    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    merged_df['CALCULATED_SOCIAL_DEDUC'].fillna(0.0)

    merged_df['CHECK_DEDUCTION'] = merged_df['SOCIAL_PEN_FUND_CONTRIP_DED'].astype(float).astype('int64') - merged_df['CALCULATED_SOCIAL_DEDUC'].astype(float).astype('int64')
    # merged_df = merged_df.round({'SOCIAL_DEDUCTION': 3})

    # merged_df= merged_df.round({'CHECK_PENSION': 3})
    # merged_df['CHECK_DEDUCTION'] = np.trunc(1000 * merged_df['CHECK_DEDUCTION']) / 1000

    merged_df['PERCENTAGE'] = merged_df['SOCIAL_PEN_FUND_CONTRIP_DED'] / (merged_df['SOCIAL_ALLOW'])
    merged_df['PERCENTAGE'] = round(merged_df['PERCENTAGE'], 2)
    merged_df['PERCENTAGE'] = merged_df['PERCENTAGE'] * 100
    # merged_df= merged_df.round({'PENSION_DEDUCTION': 3})
    merged_df['CALCULATED_SOCIAL_DEDUC'] = np.trunc(1000 * merged_df['CALCULATED_SOCIAL_DEDUC']) / 1000
    merged_df['PERCENTAGE'] = np.trunc(1000 * merged_df['PERCENTAGE']) / 1000


    check_social_fund = merged_df[(merged_df['NATIONALITY'].str.contains('BAHRAINI', na=False, case=False, regex=False))]
    check_social_fund = check_social_fund[(check_social_fund['PERCENTAGE'] != 6)]
    check_social_fund = check_social_fund[[ 'CPR_NO',   'BASIC_SALARY', 'SOCIAL_ALLOW','PERCENTAGE', 'CALCULATED_SOCIAL_DEDUC','SOCIAL_PEN_FUND_CONTRIP_DED']]
    check_social_fund.rename(columns=lambda x: x.replace('CALCULATED_SOCIAL_DEDUC', 'CALCULATED'), inplace=True)
    check_social_fund.rename(columns=lambda x: x.replace('SOCIAL_PEN_FUND_CONTRIP_DED', 'ACTUAL'), inplace=True)
    # check_social_fund.rename(columns=lambda x: x.replace('SOCIAL_PEN_FUND_CONTRIP_DED', 'STANDARD'), inplace=True)

    return check_social_fund


"""
This function to calculate and Unemployment Deduction if -------------
:param df: receive the employee master database as data frame
:return: employee records if there is an Invalid Unemployment Deduction
"""
def Check_Unemployment_Allowance_Deduction(df_master,df_payroll):
    # received master and payroll file


    # df_master[['BASIC_SALARY','SOCIAL','SPECIAL','DEDUCTION']]

    filtred_master_df = df_master[['CPR_NO', 'EMPLOYEE_NAME', 'POSITION_TITLE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)

    # filtred_master_df[['BASIC_SALARY','SOCIAL','SPECIAL']] = df_master[['BASIC_SALARY','SOCIAL','SPECIAL']].fillna(0.0)


    # filtred_master_df = Organize_Data_View(filtred_master_df)

    # df_payroll = pd.read_excel('C:/NAO-Payroll/application/data/MonthlyPayroll_data/admin/payroll-30082022_094926.xlsx')
    filtred_payroll_df = df_payroll[['CPR_NO', 'UNEMPLOYMENT_INSUR_DED', 'BASIC_SALARY', 'SOCIAL_ALLOW','SPECIAL_ALLOW']]
    filtred_payroll_df = Organize_Data_View(filtred_payroll_df)
    col_sum = (filtred_payroll_df['BASIC_SALARY'] + filtred_payroll_df['SOCIAL_ALLOW'] + filtred_payroll_df['SPECIAL_ALLOW']) * 0.01
    filtred_payroll_df["CALCULATED_UNEMP_DEDUCTION"] = col_sum

    # filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

    # matching employee by CPR
    merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
    merged_df['CALCULATED_UNEMP_DEDUCTION'] = merged_df['CALCULATED_UNEMP_DEDUCTION'].fillna(0.0)
    # merged_df = Organize_Data_View(merged_df)

    merged_df['CHECK_UNEMPLOYMENT'] = (merged_df['UNEMPLOYMENT_INSUR_DED'].astype(float).astype('int64')- merged_df['CALCULATED_UNEMP_DEDUCTION'].astype(float).astype('int64'))
    # merged_df = merged_df.round({'CHECK_UNEMPLOYMENT': 3})
    merged_df['CHECK_UNEMPLOYMENT'] = np.trunc(1000 * merged_df['CHECK_UNEMPLOYMENT']) / 1000

    merged_df['PERCENTAGE'] = merged_df['UNEMPLOYMENT_INSUR_DED'] / (merged_df['SOCIAL_ALLOW']+ merged_df['SPECIAL_ALLOW'] + merged_df['BASIC_SALARY'])
    merged_df['PERCENTAGE'] = round(merged_df['PERCENTAGE'],2)
    merged_df['PERCENTAGE'] = merged_df['PERCENTAGE']*100
    # merged_df= merged_df.round({'PENSION_DEDUCTION': 3})
    merged_df['CALCULATED_UNEMP_DEDUCTION'] = np.trunc(1000 * merged_df['CALCULATED_UNEMP_DEDUCTION']) / 1000
    merged_df['PERCENTAGE'] = np.trunc(1000 * merged_df['PERCENTAGE']) / 1000

    check_unemployment_fund = merged_df[(merged_df['PERCENTAGE'] != 1)]
    check_unemployment_fund = check_unemployment_fund[['CPR_NO','BASIC_SALARY', 'SOCIAL_ALLOW','SPECIAL_ALLOW','PERCENTAGE','CALCULATED_UNEMP_DEDUCTION','UNEMPLOYMENT_INSUR_DED']]
    check_unemployment_fund.rename(columns=lambda x: x.replace('CALCULATED_UNEMP_DEDUCTION', 'CALCULATED'), inplace=True)
    check_unemployment_fund.rename(columns=lambda x: x.replace('UNEMPLOYMENT_INSUR_DED', 'ACTUAL'), inplace=True)

    # to show data in organized way
    # check_unemployment_fund = Organize_Data_View(check_unemployment_fund)
    return check_unemployment_fund




""" Allowance Section """
# Some allowance function are in other file named LivSoviHous_data_preprocessing

def Prepare_Employee_Information_report(master_df,file_name,msheetname,payroll_df):
    """
    Excel Report of Employee Information Auditing Results
    This function responsible to prepare an excel file with dynamic sheet name if check box is checked (Employee Information Auditing Results)

    Parameters
    ----------
    master_df: the dataframe that has been selected by the end user to apply auditing process on employee information
    file_name: the name used to generate meaningful name for the generated excel file

    Returns
    -------
    """
    #list_swichedon_values = ['checkDuplicateName', 'checkMissingName', 'checkInvalidCPR', 'checkDuplicateCPR', 'checkDuplicateAccNo', 'checkInvalidAccNo', 'checkInvalidAge', 'checkInvalidALeave', 'checkInvalidSLeave', 'checkCarTransport', 'checkDuplicatHighRanking']

    # sheet_names = [list_swichedon_value.replace('check', '') for list_swichedon_value in list_swichedon_values]
    sheet_names = ['DuplicateName', 'MissingName', 'InvalidCPR', 'DuplicateCPR', 'DuplicateAccNo', 'InvalidAccNo', 'InvalidAge', 'InvalidALeave',
                   'InvalidSLeave', 'DuplicatHighRanking','MissingGrade','MissingMaterialStatus','EmployeeNotInPayroll','EmployeeNotInMaster']
    gen_report_path = generate_report_path()
    filePath = gen_report_path+file_name+'_Auditing_Result_Report.xlsx'
    writer = pd.ExcelWriter(filePath, engine="xlsxwriter")

    for sheet_name in sheet_names:
        if sheet_name == 'DuplicateName':
            #Fetch Results if DuplicateName switch button checked and write them in excel report
            result_df = Check_Duplicate_Name(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)

        if sheet_name == 'MissingName':
            """Fetch Results if MissingName switch button checked and write them in excel report"""
            result_df = Check_Missing_Name(master_df)

            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)

        if sheet_name == 'InvalidCPR':
            """Fetch Results if InvalidCPR switch button checked and write them in excel report"""
            result_df = Check_Invalid_CPR(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'DuplicateCPR':
            """Fetch Results if DuplicateCPR switch button checked and write them in excel report"""
            result_df = Check_Duplicate_CPR(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'DuplicateAccNo':
            """Fetch Results if DuplicateAccNo switch button checked and write them in excel report"""
            result_df = Check_Duplicate_Accont_No(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'InvalidAccNo':
            """Fetch Results if InvalidAccNo switch button checked and write them in excel report"""
            result_df = Check_Invalid_Account_No(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'InvalidAge':
            """Fetch Results if InvalidAge switch button checked and write them in excel report"""
            result_df = Check_Age(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'InvalidALeave':
            """Fetch Results if InvalidALeave switch button checked and write them in excel report"""
            result_df = Check_Annual_leave(master_df,msheetname)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'InvalidSLeave':
            """Fetch Results if InvalidSLeave switch button checked and write them in excel report"""
            result_df = Check_Sick_leave(master_df,msheetname)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'DuplicatHighRanking':
            """Fetch Results if DuplicatHighRanking switch button checked and write them in excel report"""
            result_df = Check_High_Rank_Posisiton(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'MissingGrade':
            """Fetch Results if MissingGrade switch button checked and write them in excel report"""
            result_df = Missing_GRADE(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'MissingMaterialStatus':
            """Fetch Results if MissingGrade switch button checked and write them in excel report"""
            result_df = Missing_MARITAL_STATUS(master_df)
            if not result_df.empty:
                """Load data into excel"""
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        # the reports the show employees who are not in payroll and vice versa
        result_master, result_payroll = Missing_Employee(master_df, payroll_df)
        if sheet_name == 'EmployeeNotInPayroll':
            if not result_master.empty:
                result_master.to_excel(writer, sheet_name=sheet_name, index=False)
        if sheet_name == 'EmployeeNotInMaster':
            if not result_payroll.empty:
                result_payroll.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.save()




def Prepare_Employee_Deduction_report(master_df,  payroll_file_path,file_name):
    """
    Excel Report of Employee Deduction Auditing Results
    This function responsible to prepare an excel file with dynamic sheet name if check box is checked (Employee deduction Auditing Results)

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
    gen_report_path = generate_report_path()
    filePath = gen_report_path + file_name + '_Auditing_Result_Report.xlsx'
    writer = pd.ExcelWriter(filePath, engine="xlsxwriter")
    global result_df
    for path in payroll_file_path:
        result_df = pd.DataFrame()
        sheetname, payroll_df = Import_Payroll_Data(path)
        payroll_df = Organize_Data_View((payroll_df))
        #Auditing Pension Allowance
        result_df = Check_Pension_Allowance(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] +'PensionAllowanceDeduc'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        #Auditing Social Allowance Deduction
        result_df = Check_Social_Allowance_Deduction(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0]+ 'SocialAllowanceDeduc'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

        #Auditing Unemployment Allowance Deduction
        result_df = Check_Unemployment_Allowance_Deduction(master_df, payroll_df)
        if not result_df.empty:
            merged_sheet_name = sheetname[0] + 'UnemploymentDeduc'
            """Load data into excel"""
            result_df.to_excel(writer, sheet_name=merged_sheet_name, index=False)

    writer.save()








