"""
Filename: application\auth\util.py

Purpose: To verify a provided password against a stored password using PBKDF2-HMAC-SHA256 algorithm.

Dependencies: hashlib, binascii

Code structure:

The function verify_pass takes two arguments: provided_password and stored_password.
The stored_password is first decoded from ASCII encoding.
The salt is extracted from the first 64 characters of the stored_password.
The actual stored password is extracted from the remaining characters of the stored_password.
PBKDF2-HMAC-SHA256 algorithm is used to hash the provided_password using the salt and 100000 iterations.
The resulting hash is converted to ASCII encoding using binascii.hexlify.
The function returns True if the provided_password matches the stored_password, else False.
"""
import binascii
import hashlib


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return provided_password == stored_password
