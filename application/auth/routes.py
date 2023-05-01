"""
Filename: application\auth\routes.py

Purpose: This file contains the routes and functions related to user authentication, including login, registration, and logout.

Dependencies:

Flask (version not specified)
Flask-Login (version not specified)
Flask-Limiter (version not specified)
Flask-WTF (version not specified)
Werkzeug (version not specified)
Code structure:

Import necessary modules and packages
Define the default route to redirect to the login page
Set up rate limiting for login attempts
Set up CSRF protection
Define the login route, which handles both GET and POST requests
Define the user_loader and request_loader functions for Flask-Login
Define the logout route
Define error handlers for various HTTP error codes and CSRF errors.
"""

import pytz
from flask import render_template, redirect, request, url_for, current_app, session
from flask_login import (
    current_user,
    login_user,
    logout_user
)
from flask_principal import RoleNeed, Identity, identity_loaded, UserNeed, identity_changed, AnonymousIdentity

from application import login_manager
from application.auth import blueprint
from application.auth.forms import LoginForm
from application.models import User
from werkzeug.security import check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime,timedelta
limiter = Limiter(key_func=get_remote_address)
MAX_LOGIN_ATTEMPTS = 5

@blueprint.route('/')
def route_default():
    return redirect(url_for('auth_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit(f'{MAX_LOGIN_ATTEMPTS} per minute')
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        remaining = int(request.headers.get("X-RateLimit-Remaining", -1))
        if remaining == 0:
            return render_template('home/page-expired.html'), 429

        # read form data
        username = request.form['username']
        # username=sanitize_input(username)
        password = request.form['password']

        print(username)
        print(password)

        # Locate user
        user = User.query.filter_by(username=username).first()

        print(user)
        session['login_attempts'] = session.get('login_attempts', 0) + 1
        session['timestamp'] = session.get('timestamp', datetime.now(pytz.utc))
        # print(session['login_attempts'])
        # print(session['timestamp'])
        # print(session['timestamp'] + timedelta(minutes=10))
        # print(datetime.now(pytz.utc))
        # print(session['timestamp'] + timedelta(minutes=10) > datetime.now(pytz.utc))
        if (session['login_attempts'] >= MAX_LOGIN_ATTEMPTS) and (session['timestamp'] + timedelta(minutes=10) > datetime.now(pytz.utc)):
            return render_template('home/page-expired.html',
                                   segment='login',
                                   msg='لقد تجاوزت الحد المسموح لمحاولات الدخول',
                                   form=login_form)

        # Check the password
        if user and check_password_hash(user.password, password) :
            login_user(user)
            session['logged_in'] = True
            session['login_attempts'] = 0
            session['timestamp']=datetime.now(pytz.utc)
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.user_id))
            return redirect(url_for('auth_blueprint.route_default'))
        else:
            if session['login_attempts'] >= MAX_LOGIN_ATTEMPTS:
                return render_template('home/page-expired.html',
                                       segment='login',
                                       msg='لقد تجاوزت الحد المسموح لمحاولات الدخول',
                                       form=login_form)
            else:
                return render_template('auth/login.html',
                                       segment='login',
                                       msg='هناك خطأ في اسم المستخدم أو كلمة المرور',
                                       form=login_form)

    if not current_user.is_authenticated:
        return render_template('auth/login.html',
                               segment='login',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@login_manager.user_loader
def user_loader(user_id):
    return User.query.filter_by(user_id=user_id).first()


@login_manager.request_loader
def request_loader(login_request):
    username = login_request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


@blueprint.route('/logout')
def logout():
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    for key in ['start', 'end']:
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(url_for('auth_blueprint.login'))


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'user_id'):
        identity.provides.add(UserNeed(current_user.user_id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
