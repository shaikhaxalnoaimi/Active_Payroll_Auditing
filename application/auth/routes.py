from flask import render_template, redirect, request, url_for
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


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    val = is_trial()
    if val == 'valid':
        login_form = LoginForm(request.form)
        if 'login' in request.form:

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
                return redirect(url_for('auth_blueprint.route_default'))

            # Something (user or pass) is not ok
            return render_template('auth/login.html',
                                   segment='login',
                                   msg='Username or Password is Incorrect',
                                   form=login_form)

        if not current_user.is_authenticated:
            return render_template('auth/login.html',
                                   segment='login',
                                   form=login_form)
        return redirect(url_for('home_blueprint.index'))

    elif val == 'expired':
        return render_template('layouts/base_expired.html',
                               segment='Expired')

    else:
        return render_template('home/page-500.html',
                               segment='No Internet')


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


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
