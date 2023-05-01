"""
(C) NAIRDC 2022
Author(s): SAMAH FUJO
Created:
15/9/2022
Last Update:
dd/mm/yyyy
By: 
SAMAH FUJO
Version:
1.0
...
File summary

This file will have all functions related to the overtime auditing process

This code depends on the following modules and functions:

os module
pandas module
generate_report_path function from application module
generate_high_position_file_path function from application module
Import_Payroll_Data function from application.home.data_processing module
Organize_Data_View function from application.home.data_processing module
organized_overtime_file function from application module

"""
import os
import pandas as pd
from application import generate_report_path,generate_high_position_file_path

from application.home.data_processing import Import_Payroll_Data, Organize_Data_View
from application import organized_overtime_file

def check_overtime( df_master,payroll_file_path):
    """

    Parameters
    ----------
    payroll_file_path the path for selected payroll files
    df_master the selected master data

    Returns
    -------
    two reports the employee who are taking overtime more than three month
    """

    # Overtime_folder = os.path.join(BASE_DIR, "data", "Overtime Rules")
    Overtime_folder = organized_overtime_file()

    # read file have list of all grade that only need to apply concept of overtime
    file_path = os.path.join(Overtime_folder, "AcceptedGrade.xlsx")
    accepted_grade = pd.read_excel(file_path)
    # path = 'C:\nao-payroll-deployment-dock\NAO-Payroll\application\data\Overtime Rules'
    accepted_grade = list(accepted_grade['Grade'])
    regular_overtime_results = pd.DataFrame()
    holiday_overtime_results = pd.DataFrame()

    final_summary_regualr_overtime = pd.DataFrame()
    final_summary_holiday_overtime = pd.DataFrame()

    # filter df
    filtred_master_df = df_master[['CPR_NO', 'POSITION_TITLE', 'GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    for payroll_file in payroll_file_path:
        sheetname, payroll_df = Import_Payroll_Data(payroll_file)


        filtred_payroll_df = payroll_df[['CPR_NO', 'REGULAR_OVERTIME', 'HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS','REGULAR_OT_HOURS']]
        filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

        # matching employee by CPR
        merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")

        if not merged_df.empty:
            filter_grade = pd.DataFrame() # to concat all results based on grade
            # search and get all employees with grades that need to check their overtime
            for i in range(len(accepted_grade)):
                filtried_emp_grade = merged_df[merged_df['GRADE'].str.contains(accepted_grade[i], na=False,case=False,regex=False)]

                if not filtried_emp_grade.empty:
                    # append results in one df
                    filter_grade = pd.concat([filtried_emp_grade,filter_grade])

            # print(filter_grade)
            # if filter_grade['REGULAR_OVERTIME']
            if not filter_grade.empty:
                # get all employees who have regular overtime
                check_regular_overtime = filter_grade[(filter_grade['REGULAR_OVERTIME'] != 0) | (filter_grade['REGULAR_OT_HOURS'] != 0)]
                # add month name for each payroll df
                check_regular_overtime['MONTH-YEAR'] = sheetname[0]

                # get all employees who have holiday overtime
                check_holiday_overtime = filter_grade[(filter_grade['HOLIDAY_OVERTIME'] != 0) |  (filter_grade['HOLIDAY_OT_HOURS'] != 0)]
                # add month name for each payroll df
                check_holiday_overtime['MONTH-YEAR'] = sheetname[0]

                # append results for both regular and holiday overtime separately
                regular_overtime_results= pd.concat([check_regular_overtime,regular_overtime_results])
                holiday_overtime_results = pd.concat([check_holiday_overtime, holiday_overtime_results])
            # print(overtime_results)
        else:
            final_summary_regualr_overtime = pd.DataFrame(columns=['CPR_NO', 'POSITION_TITLE', 'GRADE','REGULAR_OVERTIME','REGULAR_OT_HOURS'])
            final_summary_holiday_overtime = pd.DataFrame(columns=['CPR_NO', 'POSITION_TITLE', 'GRADE','HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS'])
    if not regular_overtime_results.empty:
        ##### Final regualr overtime #####
        final_regualr_cprs = []
        # fetch the number of occurrence based on cpr_no
        count_regular_occ = pd.DataFrame(regular_overtime_results.pivot_table(columns=['CPR_NO'], aggfunc='size'))
        # print(count_regular_occ.head(20))

        for i in range(len(count_regular_occ)):
            if count_regular_occ[0].values[i] >= 3:
                # print(count_regular_occ[0].values[i])
                # get all cprs who have overtime more than or equal 3 times
                final_regualr_cprs.append(count_regular_occ.index[i])
            # print(count_regular_occ[0].values[i])

        # print(regular_overtime_results.head(20))
        for final_regualr_cpr in final_regualr_cprs:
            final_summary_regualr_overtime = pd.concat([regular_overtime_results[regular_overtime_results['CPR_NO'] == final_regualr_cpr], final_summary_regualr_overtime])

    else:
        final_summary_regualr_overtime = pd.DataFrame(columns=['CPR_NO', 'POSITION_TITLE', 'GRADE', 'REGULAR_OVERTIME','REGULAR_OT_HOURS'])


    if not holiday_overtime_results.empty:
        final_holiday_cprs = []
        # fetch the number of occurrence based on cpr_no
        count_holiday_occ = pd.DataFrame(holiday_overtime_results.pivot_table(columns=['CPR_NO'], aggfunc='size'))
        for i in range(len(count_holiday_occ)):
            if count_holiday_occ[0].values[i] >= 3:
                # get all cprs who have overtime more than or equal 3 times
                final_holiday_cprs.append(count_holiday_occ.index[i])
            # print(count_regular_occ[0].values[i])


        for final_holiday_cpr in final_holiday_cprs:
            final_summary_holiday_overtime = pd.concat([holiday_overtime_results[holiday_overtime_results['CPR_NO'] == final_holiday_cpr],
                 final_summary_holiday_overtime])
    else:
        final_summary_holiday_overtime = pd.DataFrame(columns=['CPR_NO', 'POSITION_TITLE', 'GRADE', 'HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS'])


    if not final_summary_regualr_overtime.empty:
        final_summary_regualr_overtime = final_summary_regualr_overtime[['CPR_NO', 'POSITION_TITLE', 'GRADE', 'REGULAR_OVERTIME','REGULAR_OT_HOURS','MONTH-YEAR']]

    if not final_summary_holiday_overtime.empty:
        final_summary_holiday_overtime = final_summary_holiday_overtime[['CPR_NO', 'POSITION_TITLE', 'GRADE', 'HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS','MONTH-YEAR']]


    # final_summary_regualr_overtime = Organize_Data_View(final_summary_regualr_overtime)
    # final_summary_holiday_overtime = Organize_Data_View(final_summary_holiday_overtime)
    if not final_summary_holiday_overtime.empty:
        final_summary_holiday_overtime = final_summary_holiday_overtime.drop_duplicates( keep='last')
    if not final_summary_regualr_overtime.empty:
        final_summary_regualr_overtime = final_summary_regualr_overtime.drop_duplicates(keep='last')
    return final_summary_regualr_overtime, final_summary_holiday_overtime



def notAllowedOvertime(df_master,payroll_file_path):
    """
    Parameters
    ----------
    payroll_file_path the path for selected payroll files
    df_master the selected master data

    Returns
    -------
`   report display employees who are taking overtime and their grade E4-E7 and report should shows position title for any month
    """

    # Generate high position rules file path
    file_path = generate_high_position_file_path()
    # the not acceptance grade from E4 TO E7
    accepted_grade = pd.read_excel(file_path + '/AcceptanceGrade.xlsx')
    accepted_grade = '|'.join(accepted_grade['Grade'].tolist())

    # filter df
    filtred_master_df = df_master[['CPR_NO', 'POSITION_TITLE', 'GRADE']]
    filtred_master_df = Organize_Data_View(filtred_master_df)
    not_allowed_overtime = pd.DataFrame(columns = ['CPR_NO','REGULAR_OVERTIME', 'HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS','REGULAR_OT_HOURS'])
    final_results = pd.DataFrame()
    for payroll_file in payroll_file_path:
        sheetname, payroll_df = Import_Payroll_Data(payroll_file)

        filtred_payroll_df = payroll_df[['CPR_NO','REGULAR_OVERTIME', 'HOLIDAY_OVERTIME','HOLIDAY_OT_HOURS','REGULAR_OT_HOURS']]
        filtred_payroll_df = Organize_Data_View(filtred_payroll_df)

        # matching employee by CPR
        merged_df = pd.merge(filtred_master_df, filtred_payroll_df, on="CPR_NO")
        if not merged_df.empty:
            not_allowed_overtime_g = merged_df[(merged_df['GRADE'].str.contains(accepted_grade, na=False, case=False, regex=True))]
            not_allowed_overtime_n = merged_df[(merged_df['GRADE'] == 'N')]

            not_allowed_overtime = pd.concat([not_allowed_overtime_g, not_allowed_overtime_n], axis=0)

            not_allowed_overtime2 = not_allowed_overtime[((not_allowed_overtime['REGULAR_OVERTIME'] != 0 )| (not_allowed_overtime['REGULAR_OT_HOURS'] !=0)) | ( (not_allowed_overtime['HOLIDAY_OVERTIME'] != 0) | (not_allowed_overtime['HOLIDAY_OT_HOURS'] !=0 ))]

            if not not_allowed_overtime2.empty:
                final_results = pd.concat([not_allowed_overtime2,final_results])
            print(final_results)
    # if  not_allowed_overtime.empty:
    #     not_allowed_overtime = pd.DataFrame(columns = ['CPR_NO','POSITION_TITLE', 'GRADE', 'REGULAR_OVERTIME', 'HOLIDAY_OVERTIME'])

    return final_results


def Prepare_Employee_Overtime_report(master_df, payroll_file_path, file_name):
    """
    Excel Report of Employee Overtime Auditing Results
    This function responsible to prepare an excel file with dynamic sheet name if check box is checked (Employee Overtime Auditing Results)

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
    # file_name = 'Employee_info'

    gen_report_path= generate_report_path()
    # filePath = '/NAO-Payroll/application/data/Generated Report/' + file_name + '_Auditing_Result_Report.xlsx'
    writer = pd.ExcelWriter(gen_report_path+ file_name + '_Auditing_Result_Report.xlsx' , engine="xlsxwriter")

    # Auditing Car & transport Allowance
    final_summary_regualr_overtime, final_summary_holiday_overtime = check_overtime(master_df,payroll_file_path)
    not_allowed_overtime = notAllowedOvertime(master_df,payroll_file_path)
    # print(final_summary_regualr_overtime)
    if not final_summary_regualr_overtime.empty:
        merged_sheet_name =  'RegularOvertime'
        final_summary_regualr_overtime.to_excel(writer, sheet_name=merged_sheet_name, index=False)
    if not final_summary_holiday_overtime.empty:
        merged_sheet_name =  'HolidayOvertime'
        final_summary_holiday_overtime.to_excel(writer, sheet_name=merged_sheet_name, index=False)
    if not not_allowed_overtime.empty:
        merged_sheet_name = 'NotAllowedOvertime'
        not_allowed_overtime.to_excel(writer, sheet_name=merged_sheet_name, index=False)

    writer.save()



