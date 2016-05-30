from flask import Blueprint, request, jsonify, session
from flask_login import login_required
from model import *
from config import *
# from server import login_manager
user = Blueprint('user', __name__)


# @user.route('/api/avatar', method=['GET'])
# def get_user_avatar():
#     id = request.args.get('id')
#     return id
#
#
# @user.route('/api/avatar', method=['POST'])
# def set_user_avatar():


@user.route('/api/nickname', methods=['GET', 'POST'])
@login_required
def user_nickname():
    # we use GET method to request user's nickname by id
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        nickname = db.user_nickname(user_id)
        if nickname is not None:
            return jsonify({'status': 1, 'nickname': nickname})
        else:
            return jsonify({'status': -1, 'message': 'bad user id'})
    # we use POST method to modify user's nickname
    elif request.method == 'POST':
        nickname = request.form.get('nickname')
        if db.user_nickname(current_user.id) is not None:
            db.user_nickname(current_user.id, nickname)
            return jsonify({'status': 1})


@user.route('/api/addfriend')
@login_required
def user_addfriend():
    if request.method == 'GET':
        email = request.args.get('email')
        if email is not None:
            id = db.account_id(email)
            if id is not None:
                user_nickname = db.user_nickname(id)
                return jsonify({'status': 1, 'message': 'success', 'uesr_id': id, 'user_nickname': user_nickname})
            else:
                return jsonify({'status': -2, 'message': 'email address does not exist'})
        else:
            return jsonify({'status': -1, 'message': 'email address error'})
    elif request.method == 'POST':
        requester_id = current_user.id
        responser_id = request.form.get('responser_id')
        if responser_id in db.user_friendlist(requester_id):
            return jsonify({'status': -1, 'message': 'user already in requester\'s friendlist'})
        else:
            db.user_friendlist(requester_id, responser_id)
            return jsonify({'status': 1, 'message': 'success'})
    else:
        raise Exception('bad request method')


@user.route('/api/addgroup', methods=['POST'])
@login_required
def user_addgroup():
    if request == 'POST':
        group_name = request.form.get('group_name')
        if group_name == '':
            return jsonify({'status': -1, 'message': 'empty group name'})
        db.user_friendgroup(current_user.id, group_name)


# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)



class User:

    def __init__(self, id=None):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        # print id
        if id is not None:
            self.email = db.account_email(id)
            self.id = id
            self.password = db.account_password(id)
            self.nickname = db.user_nickname(id)
            self.friendgroup = db.user_friendgroup(id)
        # elif email is not None:
        #     self.email = email
        #     self.id = db.account_id(email)
        #     self.password = db.account_password(id)
        #     self.nickname = db.user_nickname(id)
        #     self.friendgroup = db.user_friendgroup(id)
        else:
            raise Exception()

    def get_id(self):
        return unicode(self.id)