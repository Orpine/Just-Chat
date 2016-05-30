import flask
from flask import Blueprint, request, session, jsonify, render_template
from model import *

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length
from flask_login import login_user
from user import User


class LoginForm(Form):
    email = StringField('Email address', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [Length(min = 6, max = 20, message = 'Password Length should between 6 and 20')])
    remember = BooleanField('Remember me')

class RegisterForm(Form):
    email = StringField('Email address', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [Length(min = 6, max = 20, message = 'Password Length should between 6 and 20')])
    nickname = StringField('nickname')


account = Blueprint('account', __name__)


@account.route('/', methods=['GET'])
def account_main():
    form_register = RegisterForm()
    form_login = LoginForm()
    return render_template('login_register.html', form_register=form_register, form_login=form_login)


@account.route('/register', methods=['POST'])
def register_process():
    # form = request.form.get('register-form')
    form = RegisterForm()
    # if email is not None and password is not None and check_register_info(email, password):
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        nickname = form.nickname.data
        if email_exist(email):
            return flask.jsonify({'status': -2, 'message': 'account already exist'})
        add_new_account(email, password, nickname)

        return flask.jsonify({'status': 1, 'message': 'register success'})
    else:
        return flask.jsonify({'status': -1, 'message': 'invalid input'})


@account.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    # form = request.form.get('login-form')
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        id = db.account_id(email)
        if id is not None and db.account_password(id) == password:
            login_user(User(id = id), remember = form.remember.data)
            return jsonify({'status': 1, 'message': 'success'})
        else:
            return jsonify({'status': -1, 'message': 'username or password error'})
    else:
        return jsonify({'status': -1, 'message': 'username or password error'})



# @account.route('/register', methods=['GET'])
# def register_page():
#     return 'you get it'

def add_new_account(email, password, nickname):
    id = db.get_new_id()
    db.account_id(email, id)
    db.account_email(id, email)
    db.account_password(id, password)
    db.user_nickname(id, nickname)
    db.user_avatar(id, 'default')
    db.user_friendgroup(id, 'My friends')


def email_exist(email):
    return db.account_id(email) is not None




