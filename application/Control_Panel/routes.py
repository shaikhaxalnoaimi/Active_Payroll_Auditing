"""
Filename: application\Control_Panel\routes.py

Purpose: This file contains the routes and functions for the control panel section of the web application. It allows the user to view, add, edit, and delete keywords and positions in the database.

Dependencies:

pandas (version 1.2.4)
Flask (version 2.0.0)
Flask-Login (version 0.5.0)
application.Control_Panel.forms (KeywrodsForm)
application.Control_Panel.keywords_db_Queries (Fetch_All_Keywords, Fetch_Lable_Keywords, Fetch_Current_Values, Edit_Keywords, Delete_Keywords, Insert_Data_Keywords)
application.Control_Panel.position_titles_db_Quires (Fetch_All_Positions, Insert_Data_Positions, Edit_Positions, Fetch_Current_Position_Values, Delete_Positions)
application.home (blueprint)
Code structure:

Import necessary libraries and modules
Define routes and functions for displaying data in the control panel section
Define routes and functions for adding data to the database
Define routes and functions for editing data in the database
Define routes and functions for deleting data from the database
"""

import pandas as pd
from flask import render_template, request, redirect, url_for, jsonify
from application.Control_Panel.forms import KeywrodsForm
from application.Control_Panel.keywords_db_Queries import Fetch_All_Keywords, Fetch_Lable_Keywords, \
    Fetch_Current_Values, Edit_Keywords, Delete_Keywords, Insert_Data_Keywords
from application.Control_Panel.position_titles_db_Quires import Fetch_All_Positions, Insert_Data_Positions, \
    Edit_Positions, Fetch_Current_Position_Values, Delete_Positions
from application.home import blueprint
from flask_login import login_required


######################################################################################-->
#####################Display Data Sctions Main Admin Panel ##############################-->
######################################################################################-->
@blueprint.route('/admin_panel', methods=["POST", "GET"])
@login_required
def admin_panel():
    keywords_form = KeywrodsForm()
    # initialize keywords_label drop down list
    keyword_labels = Fetch_Lable_Keywords("MASTER")

    keywords_form.keyword_label.choices = [(keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in
                                           keyword_labels.index]
    # initialize Keywords Table
    all_data = Fetch_All_Keywords("MASTER", "EMPLOYEE_NAME")  # based on selected label

    # initialize positions Table
    all_data_positions = Fetch_All_Positions()  # based on selected label

    if request.method == 'POST':
        # if 'file_name' in request.form and keywords_form.validate_on_submit():
        selected_fname = keywords_form.file_name.data
        selected_label = keywords_form.keyword_label.data
        all_data = Fetch_All_Keywords(selected_fname, selected_label)
        # selected keywords_label drop down list
        current_label = keywords_form.keyword_label.data
        keyword_labels = Fetch_Lable_Keywords(selected_fname)
        # print(selected_fname)
        # keywords_form.keyword_label.choices = [current_label] + [(keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in keyword_labels.index]
        keywords_form.keyword_label.choices = [(current_label, current_label)] + [
            (keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in keyword_labels.index if
            keyword_labels['LABEL'][ind] != current_label]

    return render_template('control_panel/index.html',
                           segment="Control_Panel",
                           keywords_form=keywords_form,
                           # return master keyword table filtered by label name (default selected_value)
                           all_data_mk_columns=all_data.columns.values,
                           all_data_mk_rows=list(all_data.values.tolist()),
                           # return all high ranking positions data
                           all_data_positions_columns=all_data_positions.columns.values,
                           all_data_positions_rows=list(all_data_positions.values.tolist()),
                           zip=zip
                           )


@blueprint.route('/label/<file_name>', methods=["POST", "GET"])
@login_required
def label(file_name):
    labels = Fetch_Lable_Keywords(file_name)
    labels_array = []

    for ind in labels.index:
        label_obj = {}
        label_obj['id'] = labels['LABEL'][ind]
        label_obj['label'] = labels['LABEL'][ind]
        labels_array.append(label_obj)

    return jsonify({'labels': labels_array})


######################################################
############# Adding to sqlit Section ################
######################################################
# Keywords
@blueprint.route('/add_keywords', methods=["POST", "GET"])
@login_required
def add_keywords():
    exits = ''
    keywords_form = KeywrodsForm()
    # initialize keywords_label drop down list
    # keyword_labels = Fetch_Lable_Keywords("MASTER")
    keywords_form.file_name.choices = [("", "  --- Select File Name---")] + [('MASTER', "Employee Master"),
                                                                             ('PAYROLL', 'Employee Payroll')]
    keywords_form.keyword_label.choices = [("", "  --- Select Label of Keyword ---")]
    # + [(keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind] ) for ind in keyword_labels.index]

    if request.method == 'POST':
        selected_fname = keywords_form.file_name.data
        selected_label = keywords_form.keyword_label.data
        kname = request.form['keyword']

        # update selected keywords_label drop down list
        keyword_labels = Fetch_Lable_Keywords(selected_fname)
        keywords_form.keyword_label.choices = [(keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in
                                               keyword_labels.index]

        check_message = Insert_Data_Keywords(selected_label, kname, selected_fname)
        if check_message == 'duplicate':
            exits = True
        elif check_message == 'invalid':
            exits = 'Invalid'
        else:
            exits = False

    return render_template("control_panel/add_keyword.html",
                           exits=exits,
                           keywords_form=keywords_form)


# Position
@blueprint.route('/add_position', methods=["POST", "GET"])
@login_required
def add_position():
    # only enters for get request not entering in post
    """
    The HyperText Transfer Protocol (HTTP) 400 Bad Request response status code indicates that the server cannot or will
    not process the request due to something that is perceived to be a client error (for example, malformed request
    syntax, invalid request message framing, or deceptive request routing).
    """
    print(request.method, "=" * 20)
    exits = ''
    if request.method == 'POST':
        pname = request.form['position']
        print('the position name:' + pname)
        check_message = Insert_Data_Positions(pname)
        # print('recived mesage:' + check_message)
        if check_message == 'duplicate':
            exits = True
        elif check_message == 'invalid':
            exits = 'Invalid'
        else:
            exits = False

    return render_template("control_panel/add_position.html",
                           exits=exits)


######################################################
############# Editing on sqlit Section ################
######################################################
# edit keyword
@blueprint.route('/edit_keyword/<string:uid>', methods=["POST", "GET"])
@login_required
def edit_keyword(uid):
    updated = ''
    # file_name = 'MASTER'
    # master_label1 = Fetch_Lable_Keywords(file_name)

    file_name, current_label, current_keyword = Fetch_Current_Values(uid)
    # file_name = Fetch_File_Name(uid)

    keywords_form = KeywrodsForm()
    keyword_labels = Fetch_Lable_Keywords(file_name)
    # keywords_form.keyword_label.choices = [(current_label['LABEL'][ind], current_label['LABEL'][ind]) for ind in
    #                                        current_label.index] + [
    #                                           (keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in
    #                                           keyword_labels.index if
    #                                           keyword_labels['LABEL'][ind] != current_label['LABEL'][0]]
    keywords_form.keyword_label.choices = [(current_label, current_label)] + [
        (keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in
        keyword_labels.index if
        keyword_labels['LABEL'][ind] != current_label]

    if request.method == 'POST':
        select_label = keywords_form.keyword_label.data
        kname = request.form['keyword1']
        check_message = Edit_Keywords(select_label, kname, uid, file_name)

        if check_message == 'duplicate':
            updated = True
            # return updated current values
            file_name, current_label, current_keyword = Fetch_Current_Values(uid)
        elif check_message == 'invalid':
            updated = 'Invalid'
        else:
            updated = False

    return render_template("control_panel/edit_keyword.html",
                           uid=uid,
                           updated=updated,
                           current_label=current_label,
                           current_keyword=current_keyword,
                           keywords_form=keywords_form,
                           )


# edit position
@blueprint.route('/edit_position/<string:uid>', methods=["POST", "GET"])
@login_required
def edit_position(uid):
    updated = ''
    current_position = Fetch_Current_Position_Values(uid)
    if request.method == 'POST':
        pname = request.form['position1']
        check_message = Edit_Positions(pname, uid)

        if check_message == 'duplicate':
            updated = True
            # return updated current values
            current_position = Fetch_Current_Position_Values(uid)
        elif check_message == 'invalid':
            updated = 'Invalid'
        else:
            updated = False

    return render_template("control_panel/edit_position.html",
                           uid=uid,
                           updated=updated,
                           current_position=current_position)


######################################################
############# Deleting form sqlit Section ################
######################################################
# deleting keyword
@blueprint.route('/delete_keyword/<string:uid>/<string:selected_value>/<string:fname>', methods=['GET'])
@login_required
def delete_keyword(uid, selected_value, fname):
    all_data = pd.DataFrame()
    deleted = False
    keywords_form = KeywrodsForm()
    # selected keywords_label drop down list
    # current_label = keywords_form.keyword_label.data
    keyword_labels = Fetch_Lable_Keywords(fname)

    keywords_form.keyword_label.choices = [(selected_value, selected_value)] + [
        (keyword_labels['LABEL'][ind], keyword_labels['LABEL'][ind]) for ind in keyword_labels.index if
        keyword_labels['LABEL'][ind] != selected_value]

    Delete_Keywords(uid)
    deleted = True
    # updated list after deleting
    all_data = Fetch_All_Keywords(fname, selected_value)

    print(selected_value)
    print(fname)

    return redirect(url_for('control_panel.admin_panel'))

    # deleted = True
    # #updated list after deleting
    #
    # all_data = Fetch_All_Keywords(current_label,fname)

    # return render_template('control_panel/index.html',
    #                        segment="Control_Panel",
    #                        # return true to show message that the rwo deleted successfully
    #                        deleted = deleted,
    #                        # return the same label that the keyword you try to delete is belong to it to reflect the change after deleting on table with sam label
    #                        # selected_value = selected_value,
    #
    #                        keywords_form=keywords_form,
    #                        all_data_mk_columns=all_data.columns.values,
    #                        all_data_mk_rows=list(all_data.values.tolist()),
    #                        zip=zip
    #                        )

    # return redirect(url_for("control_panel.index"))


# deleting position
@blueprint.route('/delete_position/<string:uid>', methods=['GET'])
@login_required
def delete_position(uid):
    Delete_Positions(uid)
    return redirect(url_for('control_panel.admin_panel'))
