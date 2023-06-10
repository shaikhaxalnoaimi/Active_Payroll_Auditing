# Define a function to join file paths securely
import os


def secure_join(*args):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(BASE_DIR, *args)
    return os.path.abspath(os.path.normpath(path))

