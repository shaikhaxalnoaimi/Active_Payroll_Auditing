"""
Filename: application\Control_Panel\validation.py

Purpose: This module provides functions to validate and sanitize user input.

Dependencies:

re (built-in)
html (built-in)
bleach (version 3.3.0)
Code structure:

is_valid_input(input): function to check if a keyword is valid
sanitize_input(user_input): function to sanitize user input by removing or modifying any potentially harmful or unwanted characters or code from user input.
"""

import os
import re
import html
import bleach

def is_valid_input(input):
    """
    Check if a keyword is valid.
    """
    if not input:
        return False
    allowed_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    return set(input) <= allowed_characters



def sanitize_input(user_input):
    """
    Sanitizing user input involves removing or modifying any potentially harmful or unwanted characters or code from user input.
    Parameters
    ----------
    user_input

    Returns
    -------
        sanitized_input
    """
    # Replace &, <, >, ", ' with their HTML entities using the html.escape() function
    sanitized_input = html.escape(user_input)

    # Remove any leading or trailing whitespace
    sanitized_input = bleach.clean(sanitized_input, strip=True)
    # Remove any non-alphanumeric characters and underscores
    sanitized_input = re.sub(r'[^a-zA-Z0-9_]', '', sanitized_input)

    return sanitized_input




