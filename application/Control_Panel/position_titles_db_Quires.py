# import sqlite3
# import pandas as pd
from flask_login import  current_user
# from datetime import datetime
# from application import db_path
# from application.Control_Panel.validation import is_valid_input,sanitize_input
import pandas as pd

from .. import db
from ..models import system_high_ranking_positions
def Fetch_All_Positions():
    """
    This function to Fetch all high ranking positions title
    :return all keywords df
    """

    all_data = system_high_ranking_positions.Fetch_All_Positions_dataframe(system_high_ranking_positions)
    print(all_data)
    return all_data


def Insert_Data_Positions(position_title):
    """
    This function to add new high ranking positions
    :param: receive the selected label and entered keyword from forms
    :return a df this dataframe will have data if the added keyword already exists and empty if added keyword is successful and no duplicate
    """
    # print('the position title entered:' + position_title)
    created_by = current_user.username
    # print('The one who add' + created_by)
    #fetch data if it is already exist in position table
    validate = system_high_ranking_positions.Add_position_check_not_exist(position_title,created_by)

    return validate


def Edit_Positions(position_title,uid):
    """
    This function to edit high ranking positions
    :param: receive the id of position title
    :return a df this dataframe will have data if the edited positions already exists and empty if added positions is successful and no duplicate
    """
    position_title = position_title.upper()
    updated_by = current_user.username
    validate = system_high_ranking_positions.Update_position_by_id(uid, position_title, updated_by)
    return validate



def Fetch_Current_Position_Values(uid):
    """
    This function to Fetch current position
    :param position id
    :return position_title
    """
    current_position = system_high_ranking_positions.Fetch_poistion_by_id(uid)
    return current_position.position_title



def Delete_Positions(uid):
    """
    This function to delete the position title based on id
    :param: receive the id of position title
    :return nothing
    """
    # with sqlite3.connect(db_path) as cur:
    system_high_ranking_positions.Delete_position_by_id(uid)

def fetchAllPositionTitle():
    """
    This function fetches all high ranking positions based on the selected label.

    Returns
    -------
    all_data: list
        a list of all high ranking positions title
    """
    all_data = system_high_ranking_positions.Fetch_All_position_in_list()

    return all_data


