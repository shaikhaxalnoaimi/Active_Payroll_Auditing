import secrets

from flask import render_template, redirect, request, url_for, session
from application.Control_Panel.validation import sanitize_input
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from application import login_manager
from application.auth import blueprint
from application.auth.forms import LoginForm
from application.models import User
from werkzeug.security import check_password_hash

from application.test_version import is_trial
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect,CSRFError


@blueprint.route('/')
def route_default():
    val = is_trial()
    if val == 'valid':
        return redirect(url_for('auth_blueprint.login'))
    elif val == 'expired':
        return render_template('layouts/base_expired.html',
                               segment='Expired')

    else:
        return render_template('home/page-500.html',
                               segment='No Internet')


# Set the maximum number of login attempts per user per minute
limiter = Limiter(key_func=get_remote_address)
MAX_LOGIN_ATTEMPTS = 10
csrf = CSRFProtect()


from werkzeug.security import generate_password_hash, check_password_hash


# Login & Registration
@blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit(f'{MAX_LOGIN_ATTEMPTS}/minute')
@csrf.exempt
def login():
    login_form = LoginForm(request.form)
    if request.method == 'POST':
        # read form data
        username = request.form['username']
        password = request.form['password']

        username = sanitize_input(username)
        password = sanitize_input(password)

        # Locate user
        user = User.query.filter_by(username=username).first()


        # Check the password
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['logged_in'] = True
            session['login_attempts'] = 0

            # return redirect(url_for('auth_blueprint.route_default'))
            return redirect(url_for('home_blueprint.index'))
        else:
            # Increment the login attempt counter
            session.setdefault('login_attempts', 0)
            session['login_attempts'] += 1
            # Something (user or pass) is not ok

            print(session['login_attempts'])
        if session['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
            # Display a message indicating that the user has exceeded the maximum login attempts
            return render_template('auth/login.html',
                                   segment='login',
                                   msg='You have exceeded the maximum number of login attempts. Please try again later.',
                                   form=login_form
                                   )
        else:
            # Display a message indicating that the user's login credentials are incorrect
            return render_template('auth/login.html',
                                   segment='login',
                                   msg='Username or Password is Incorrect',
                                   form=login_form)

    else:
        return render_template('auth/login.html',
                               segment='login',
                               form=login_form)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.request_loader
def request_loader(login_request):
    username = login_request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(429)
def access_forbidden(error):
    return render_template('home/page-429.html'), 429


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


@blueprint.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('home/page-500.html', reason=e.description), 400
