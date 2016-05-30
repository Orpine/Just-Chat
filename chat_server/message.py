from flask import Blueprint
from flask_login import current_user
from flask_socketio import emit, send, join_room, leave_room
from . import socketio
from config import authenticated_only
from model import db
import time
from flask import current_app as app


# logger = logging.getLogger(__name__)
message = Blueprint('message', __name__)


@socketio.on('connect', namespace='/message')
@authenticated_only
def connect():
    db.user_online(current_user.id, set = True)
    join_room(current_user.id)
    app.logger.debug('user {} connect'.format(current_user.id))


@socketio.on('disconnect', namespace='/message')
def test_disconnect():
    if current_user.is_authenticated:
        db.user_offline(current_user.id)
        leave_room(current_user.id)
    print('Client disconnected')


@socketio.on('ready for data', namespace='/message')
def get_message(msg):
    emit('friend list data', db.user_friendgroup(current_user.id))
    emit('first response', {'data': 'Connected'})


@socketio.on('send message', namespace='/message')
def sender_send_message(data):
    message = {'message': data['message'], 'time': time.ctime()}
    sender = current_user.id
    receiver = data['receiver']
    app.logger.debug('user {} send message to {}'.format(sender, receiver))
    db.message_sent(sender = sender, receiver = receiver, message = message)
    if db.user_online(receiver) == 'True':
        emit('receive message', {'sender': sender, 'message': message}, room = receiver)
        db.message_received(sender = sender, receiver = receiver, message = message)
    else:
        db.message_processing_wating(sender = sender, receiver = receiver, message = message)
    # send_message(sender = current_user.id, receiver = data['receiver'], message = message)


@socketio.on('receive wating message', namespace = '/message')
def receiver_receive_wating_message():
    while True:
        message = db.get_wating_message(current_user.id)
        if message is None:
            break
        # send_message(sender = message['sender'], receiver = current_user.id, message = message['message'])
        sender = message['sender']
        receiver = current_user.id
        message = message['message']
        if db.user_online(receiver) == 'True':
            emit('receive message', {'sender': sender, 'message': message}, room = receiver)
            db.message_received(sender = sender, receiver = receiver, message = message)
        else:
            db.message_processing_wating(sender = sender, receiver = receiver, message = message)


# def send_message(sender, receiver, message):
#     if db.user_online(receiver) == 'True':
#         receiver_receive_message(sender, receiver, message)
#     else:
#         receiver_wait_message(sender, receiver, message)
#
#
# def receiver_receive_message(sender, receiver, message):
#     emit('receivemessage', {'sender': sender, 'message': message}, room = receiver)
#     db.message_received(sender = sender, receiver = receiver, message = message)
#
#
# def receiver_wait_message(sender, receiver, message):
#     db.message_processing_wating(sender = sender, receiver = receiver, message = message)
