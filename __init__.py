"""
Filename: __init__.py

Purpose: To join file paths securely and return the absolute path of the joined path.

Dependencies:

os module (built-in)
file variable (built-in)
Code structure:

The function secure_join() takes variable number of arguments using *args.
The BASE_DIR variable is set to the absolute path of the directory containing the current file using os.path.abspath() and os.path.dirname(file).
The path variable is set to the joined path using os.path.join() with BASE_DIR and *args as arguments.
The path is then normalized and returned as the absolute path using os.path.abspath() and os.path.normpath().
"""

# Define a function to join file paths securely
import os


def secure_join(*args):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(BASE_DIR, *args)
    return os.path.abspath(os.path.normpath(path))

# print(secure_join('data', 'nao_db.sqlite3'))