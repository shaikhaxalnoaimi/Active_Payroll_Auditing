import re


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
    # Remove any non-alphanumeric characters and underscores
    sanitized_input = re.sub(r'[^a-zA-Z0-9_]', '', user_input)

    return sanitized_input