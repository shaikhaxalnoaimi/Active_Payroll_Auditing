no_duplicate_name = True





"""--------- Employee Information Checking --------- """









""" --------- Employee Allowance deduction Checking --------- """


# ----------------------Validation------------------

""" --------- Employee Information Checking Validations --------- """
no_car_transport_allowance = Check_Auditing_Validation(car_transport_allowance)


""" --------- Employee Allowance deduction Checking Validations --------- """
no_missing_values_related_to_deduction = Check_Auditing_Validation(missing_values_related_to_deduction)
no_invalid_pension_allowance = Check_Auditing_Validation(invalid_pension_allowance)
no_invalid_social_allowance_deduction = Check_Auditing_Validation(invalid_social_allowance_deduction)
no_invalid_unemployment_allowance_deduction = Check_Auditing_Validation(invalid_unemployment_allowance_deduction)

""" --------- Employee Allowance Checking Validations --------- """
no_car_transport_allowance = Check_Auditing_Validation(car_transport_allowance)








""" --------- Returns --------- """


