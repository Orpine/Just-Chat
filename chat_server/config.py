from flask import session, jsonify
from functools import wraps


# def login_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         if not session.has_key('logged') or not session['logged']:
#             return jsonify({'status': -2, 'message': 'require login'})
#         kwargs['user_id'] = session['user_id']
#         return func(*args, **kwargs)
#     return wrapper


import functools
from flask_login import current_user
from flask_socketio import disconnect


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped