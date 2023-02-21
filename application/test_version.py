"""
(C) NAIRDC 2022
Author(s):
who are you?
Created:
dd/mm/yyyy
Last Update:
dd/mm/yyyy
By:
who are you?
Version:
1.0
...
File summary
"""
from flask_login import logout_user
from bs4 import BeautifulSoup
import urllib.request as urllib2
import requests


def connection_check():
    """
    This function to check if the server connecting to the internet or not

    Returns
    -------
        if google return successfully then will return True otherwise return False
    """

    try:
        urllib2.urlopen('https://www.google.com',timeout=4)
        return True
    except urllib2.URLError as err:
        return False


def get_internet_date():
    """
    This function to get current date from Internet (https://www.calendardate.com/todays.htm)
    Returns
    -------

    """
    r = requests.get('https://www.calendardate.com/todays.htm')
    # get html of the website
    soup = BeautifulSoup(r.text,'html.parser')
    a = soup.find_all(id='tprg')[6].get_text()
    a = a.replace('-', '')
    a = a.replace(' ','')
    return a


def is_trial():

    if connection_check() == True:
        limit = 20230331 # date when you want to close the system
        # limit = 20220928
        current_date = int(get_internet_date())
        if current_date <= limit:
            return 'valid'
        else:
            logout_user()
            return 'expired'
    else:
        return 'no internet'


