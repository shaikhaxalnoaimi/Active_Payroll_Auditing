"""
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

'''
-- Should be in environment file -- 
'''
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

    '''
    CSP is a security mechanism aimed at protecting from XSS and Clickjacking attacks. 
    CSP allows you to specify trusted origins of Javascript, fonts, CSS and others.
    If the content is not coming from the application itself then it gets disregarded. 
    '''
    # Enable Content Security Policy - CSP
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'nonce-trv5tedth15217' 'sha256-WXOrwGhmQg5d/7kVRKK6oS+feD64YaRLIi5CTNSrYwk=' 'sha256-LQstYDa3eXmrb0PvuYksXtQ6i6owZhpNsmy5nnVd/qw=' 'sha256-bbRvD22eGXhzPSKhX6OzVFoQzxfBlALvbFsxWRzRhFY=' 'sha256-TG0j76inI9XBF98Kxvd0QaZtlgz06c9M8gqr0ayYTvM='; style-src-attr 'sha256-0EZqoz+oBhx7gF4nvY2bSqoGyy4zLjNF+SDQXGp/ZrY=' 'sha256-nG1xoudMpbJeELjsW3kHtsm60dn6+RFwjddORJI/bh0=' 'sha256-zPnkVjecYfNoc7yRmyOSHpJh1SMY5ciO19WiH0Q48/M=' 'sha256-uAb603mBx+9nSJk98Qhz00aiLOql29MYaM8NHK1a/JQ=' 'sha256-bE3RL1fAlVMVfa5IjWR/H4zwiUK2m6pJP+ps/uUt6os=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-53VzmLpdouRlYsOF0JLQQ8NZFbtiZUkN5Mi1DiDjPF0=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-bE3RL1fAlVMVfa5IjWR/H4zwiUK2m6pJP+ps/uUt6os=' 'sha256-zPnkVjecYfNoc7yRmyOSHpJh1SMY5ciO19WiH0Q48/M=' 'sha256-nG1xoudMpbJeELjsW3kHtsm60dn6+RFwjddORJI/bh0=' 'sha256-kzo65yFvQxlS2MS399WhAEfCxGm9d9hOZgwRdbJw1Ec=' 'sha256-vVQqvdUbALayQcIfyV/SkciTj/E4NDENarrHaXh6uRo=' 'sha256-25ni9blovGZvhd2uk+GhMxliVLI2hgiWSSeET3t3qBg=' 'sha256-hW80QiErlj8CSNdBoQ4ZM0l5zoPPRBZSHs0GLIPyUkw=' 'sha256-JelW37ikWjqBcd6PhZa6c6VmHdShTP3s76r9QrrYRt4=' 'sha256-A3EzmwArVyCwq/3uapxFmjg0QEByxG1vie14NWjpjz4=' 'sha256-aqNNdDLnnrDOnTNdkJpYlAxKVJtLt9CtFLklmInuUAE=' 'sha256-7O10ucTTU01q8BMutjAqnHEJvL7XPRQ4D4NUYw0j+Rs=' 'sha256-nMxMqdZhkHxz5vAuW/PAoLvECzzsmeAxD/BNwG15HuA=' 'sha256-yPN+ito1tX82gEsGVGHU4q5CYwuSnIxiXnAoeBnrSYw=' 'sha256-rp8fkbtkGou1up+RrZxgBs9mXHt61ycabvB1Ak7CcS8=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-bE3RL1fAlVMVfa5IjWR/H4zwiUK2m6pJP+ps/uUt6os=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-53VzmLpdouRlYsOF0JLQQ8NZFbtiZUkN5Mi1DiDjPF0=' 'sha256-bE3RL1fAlVMVfa5IjWR/H4zwiUK2m6pJP+ps/uUt6os=' 'sha256-HPEsn1+TjMvfvUjmDbaMvlwEo6En3YA5asnR1W2xcJQ=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-7hpmv9jgnHdohqHOPs/3Bo3nqwFgI916XIggaNofuNc=' 'sha256-N90MKmRow2DpYEVeqcc3uc8pOUsS4Rg4sNmkau1k0xQ=' 'sha256-zPnkVjecYfNoc7yRmyOSHpJh1SMY5ciO19WiH0Q48/M=' 'sha256-uAb603mBx+9nSJk98Qhz00aiLOql29MYaM8NHK1a/JQ=' 'sha256-nG1xoudMpbJeELjsW3kHtsm60dn6+RFwjddORJI/bh0=' ; img-src  'self' http://www.w3.org ; font-src  'self' https://ka-f.fontawesome.com https://fonts.gstatic.com/s/roboto/v30/KFOlCnqEu92Fr1MmSU5fCRc4EsA.woff2  https://fontawesome.com ; script-src-elem https://cdnjs.cloudflare.com 'sha256-IOckPihC96tI5tOmTWBYtbqFtdQFKrQbYagqPmO4l2I=' 'sha256-IOckPihC96tI5tOmTWBYtbqFtdQFKrQbYagqPmO4l2I=' 'sha256-cmHUXF9gpLC/X2+fuuRM/0vhAF09qFPxlxai9mdlpQ8=' 'sha256-QPYCud//Y/gEqf6lABE6lT8PBTohrp7hx4HjDdmu/+M=' 'sha256-V4UjeIP8SHeeby3EEMxy4bkiEU1Ww2YVpid8+B5lEWo=' 'sha256-KW12Nf4811jAMqwaHTxeo5kTzzQa77s9CD1TfYJoRa8=' 'sha256-73t/2gLhPfDlscOu/lhHIWnpoodwHV4OS2n24tiKrQ0=' 'sha256-uOLzB79DzvVAI1ZMjq6Snoo3BG8VHOuzmXsdf2ybb/k=' 'sha256-ia/sujP+NWylSicqvlR7O7C5Qr6vWQ67gpld1fqwYQI=' 'sha256-KdyiXwVMm8HAMRuHJ30zNizz9AYVKLRmZNKGLAoXkyk=' 'sha256-csEKb0HBGxS7/gr8V3hqDhKgrppl5Ki6Be5Ekdt+ni8=' 'sha256-1BI0ZWddjeo8dag3Mq7IQwhx2aNaVk64r804sfdeGwg=' 'sha256-i1C52Cym2HEZUMrjZ5QjQSK4yu15zwu4BiDaO792yQs=' 'sha256-GDrz6tZrD37AErFBemu7HNtj2Wg4uYCDxxzJVsHuyjA=' 'sha256-73t/2gLhPfDlscOu/lhHIWnpoodwHV4OS2n24tiKrQ0=''sha256-KW12Nf4811jAMqwaHTxeo5kTzzQa77s9CD1TfYJoRa8=''sha256-uOLzB79DzvVAI1ZMjq6Snoo3BG8VHOuzmXsdf2ybb/k=' 'sha256-YOi96mXfFHn72RJU2VUINlMWSSZ+U2QhvqoCIC8hMB4=' 'sha256-IJW1UE65OI5OI/KR7IPJ4u/fWCpLPMZYaMdVw70tU68='  'sha256-maiy7k0RNtcM7iFKR/PZFjGBywfZJ7OzskhMDIpabHM=' 'sha256-cF8hiET0XUXLviXTUT8t0dDXmFqkwnxCmgY3FHKEjlY=' 'sha256-lANAWEPfEzIZBtb6OJo090v4VPKvAfHF+L3KLu56VGM=' 'sha256-PiGTlFCtIpwmo5RgVI059QidSAbleEH+P4aBX1U0JpU='  'sha256-GNew25oxT6ITUkhZs41HXtXdJ3OR+bCD0RQxjA5EsiE=' 'sha256-APTSz4MJyrLZeQjoEUPJa+2aGT4cWqzkNL9mceP9HQM=' 'sha256-Wv9oWWj1RWenFNocGFXUvPvaVMXgIAYeLZVtZ71ozGg=' 'sha256-ZRtjGgeaNIsXi3mTrQuioq0kpNLNxENGExn1VBcD5GU=' 'sha256-1jroPBTylxXhN7noFw1cj1b1kiTrJ40KKtxMIqfQyz0=' 'sha256-8qiUtVM08MLu9X6irAeoEOJ25fN9MsG/SNU4H+shU14=' 'sha256-WcYufzk7y2SbxTbQR+HdB3DsnE/cyWYlLVdnj1qX7UM=' 'sha256-UqtxFZOFgov1DX8m1oEnr6DMZ4D7zQdwsglCiW0pw7U=' 'sha256-r36AaEkN6ZiCSn7JtUmr59quAJnt2v4V5WSoaZODiUY=' 'sha256-w7ISrwYqqi20BHIENGwys469i53VDOQsxp4V83zYmaw=' 'sha256-2AhppFUi9vSHK/0LetHleMMnxKNh7vLyfQvNjCkv9eM=' 'sha256-D5vgfIi7dRo8vOv5Ufc4P0X3nesFg9n96gR2iPevPgo=' 'sha256-kCK9ZVpTVJlIHQdauW0LkObEeIBTxH/+3P1+c20KvaU=' 'sha256-Ult82X7HKT+LZPNClJdEcx1sGI3Q7cb5Ug83jof6+h8=' 'sha256-+HhwtDkgoxlXGPAywbs4Qvz1dqqEPvjeO0mYHg5MBHs=' 'sha256-3Jtctb6hVlxU+FHZqNCsRvK1Ule74+M5hRkbL5NvGQg=' 'sha256-ras+Osxt4IO72NpZQXELzG9gFy9BU041Hl1UnczkjFo=' 'sha256-bjIAIueDxoSMkijeqa+e0PWTp8Iil7W0pLoWW9yoZac=' 'sha256-tVVwd2Z/XDkNm+3uy85n+KfIW4UvYosKBh62ewpalU8=' 'self' ; script-src  'self' 'nonce-trv5tth15'   ; form-action 'self'; connect-src  https://ka-f.fontawesome.com  "

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
