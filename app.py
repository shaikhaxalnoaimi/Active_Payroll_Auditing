""""
Filename: app.py

Purpose: This file is the main entry point for the Flask application. It creates the Flask app, initializes the database, sets up security headers, and runs the app.

Dependencies with version:

Flask==1.1.2
Flask-Migrate==2.7.0
Flask-WTF==0.14.3
Flask-Limiter==1.4
secrets==1.0.2
uWSGI==2.0.20
Code structure:

Import necessary modules and packages
Create the Flask app using the create_app() function from the application package
Initialize the database migration using the Migrate() function from Flask-Migrate
Set various security headers for the app using the add_security_headers() function
Generate a secret key for CSRF protection using the secrets module
Initialize CSRF protection using the CSRFProtect() function from Flask-WTF
Define a function to join file paths securely
Run the app using the run() function from Flask, with options for host and debug mode.
"""

# import logging

from application import create_app, db
from flask_migrate import Migrate
from application.auth.routes import limiter
from flask_wtf.csrf import CSRFProtect
import secrets



app = create_app()
Migrate(app, db)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600
)

# app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeuksEkAAAAAP09FcIloKPNg9TT0pMZ-YsxNZpp'
# app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeuksEkAAAAAO33EMQ00idlooIslwdsr9qhbHW5'


# limiter = Limiter(
#     get_remote_address,
#     app=app,
#     default_limits=["200 per day", "50 per hour"],
#     storage_uri="memory://",
# )

@app.after_request
def add_security_headers(response):
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Enable content sniffing protection
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Enable Referrer-Policy
    response.headers['Referrer-Policy'] = 'no-referrer'

    # Enable strict transport security
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

    # Enable caching control
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


# Prevent the bot from login
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
csrf = CSRFProtect(app)

# Define a function to join file paths securely
if __name__ == '__main__':
    limiter.init_app(app)
    csrf.init_app(app)
    app.run(host='0.0.0.0', debug=True)
    # app.run( port=2052, debug=True)
