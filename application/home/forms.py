"""
Filename: application\home\forms.py

Purpose: This file contains the FlaskForm classes used in the web application for employee information audit and payroll processing.

Dependencies with version:

Flask (1.1.2)
Flask-WTF (0.14.3)
WTForms (2.3.3)
Code structure:

The file starts with importing necessary modules and classes from Flask, Flask-WTF, and WTForms.
Then, three FlaskForm classes are defined for different purposes:
MasterSheetForm: This class is used for uploading the employee master sheet file.
SelectMasterForm: This class is used for selecting the uploaded employee master sheet file from a dropdown list.
PayRollSheetForm: This class is used for uploading the employee payroll sheet file.
selectPayrollForm: This class is used for selecting the uploaded employee payroll sheet file from a dropdown list.
Each class contains necessary form fields and validators for the respective purpose.
The PayRollSheetForm class also contains an init method to customize the form fields dynamically based on the selected employee master sheet file.

"""


from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
# from wtforms import InputRequired
from wtforms.validators import InputRequired
# from flask_wtf import FileField, FileAllowed
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm

"""
# ======================================================================================================================
# INDEX (Employee Information Audit)
# ======================================================================================================================
"""
class MasterSheetForm(FlaskForm):
    master = FileField( validators=[InputRequired(message="Please upload Employee Master Sheet!"),
            FileAllowed(['xlsx', 'csv'], message="Please upload file with .xlsx and .csv extensions only!")])
    submit1 = SubmitField('MasterSheetForm')


"""
# ======================================================================================================================
# Fill dropdown list by uploaded employee master sheet
# ======================================================================================================================
"""
class SelectMasterForm(FlaskForm):
    directories = SelectField('directories')
    submit2 = SubmitField('SelectMasterForm')


"""
# ======================================================================================================================
# Employee Payroll Form (upload file) 
# ======================================================================================================================
"""
class PayRollSheetForm(FlaskForm):
    PayRoll = FileField(
        validators=[
            #thos messgae will not appear becuase im using clinte side message
            InputRequired(message="Please upload PayRoll Over Sheet!"),
            FileAllowed(['xlsx', 'csv'], message="Please upload file with .xlsx and .csv extensions only!"),
        ] )
    #submit1 = SubmitField('submit')


    def __init__(self, *args, **kwargs):
        super(PayRollSheetForm, self).__init__(*args, **kwargs)



"""
# ======================================================================================================================
# Fill dropdown list by uploaded employee master sheet
# ======================================================================================================================
"""
class selectPayrollForm(FlaskForm):
    directories_payroll = SelectField('directories')
    submit2 = SubmitField('selectPayrollForm')


