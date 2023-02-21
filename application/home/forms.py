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


