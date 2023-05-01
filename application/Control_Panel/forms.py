"""
Filename: application\Control_Panel\forms.py

Purpose: This file contains the implementation of a Flask form for selecting a file name and a label for a keyword.

Dependencies: This file depends on the Flask framework and the WTForms library.

Code structure:

The KeywrodsForm class is defined, which inherits from FlaskForm.
Two SelectField objects are defined within the class, one for the file name and one for the keyword label.
The choices for the file name SelectField are defined as a list of tuples, where the first element of each tuple is the value that will be submitted with the form, and the second element is the label that will be displayed to the user.
The choices for the keyword label SelectField are initially left empty, as they will be populated dynamically based on the selected file name.
Both SelectField objects have InputRequired validators attached to them, which will ensure that the user selects a value before submitting the form.
A SubmitField object is defined for submitting the form.
The form is then ready to be used in a Flask view function.
"""

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