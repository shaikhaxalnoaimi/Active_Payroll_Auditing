from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

# this form has two select filed one will fill by file names and other will fill by label
from wtforms.validators import InputRequired



class KeywrodsForm(FlaskForm):
    file_name = SelectField('file_name', choices=[('MASTER',"Employee Master"), ('PAYROLL','Employee Payroll')],
                            validators=[InputRequired(message="Please select file name!")])
    keyword_label = SelectField('keyword_label', choices=[],
                                validators=[InputRequired(message="Please select label of keyword name!")])

    submit1 = SubmitField('KeywrodsForm')