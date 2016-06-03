from flask import Blueprint
from flask_login import current_user, logout_user
from flask_socketio import emit, send, join_room, leave_room
from . import socketio
from config import authenticated_only
from model import db
import time
from flask import current_app as app
import json

# logger = logging.getLogger(__name__)
message = Blueprint('message', __name__)


@socketio.on('connect', namespace='/message')
@authenticated_only
def connect():
    db.user_online(current_user.get_id(), set = True)
    app.logger.debug('user {} connect'.format(current_user.get_id()))
    join_room(current_user.get_id())
    notification_set = db.user_notification_set(current_user.get_id())
    if notification_set is not None:
        for id in notification_set:
            emit('receive friendlist', db.user_friendlist(id), room = id)
            emit('receive friendgrouplist', db.user_friendgroup(id), room = id)


@socketio.on('disconnect', namespace='/message')
def disconnect():
    if current_user.is_authenticated:
        db.user_offline(current_user.get_id())
        leave_room(current_user.get_id())
        notification_set = db.user_notification_set(current_user.get_id())
        if notification_set is not None:
            for id in notification_set:
                emit('receive friendlist', db.user_friendlist(id), room = id)
                emit('receive friendgrouplist', db.user_friendgroup(id), room = id)
        logout_user()
        print('Client disconnected')


@socketio.on('ready for data', namespace='/message')
def first_response(msg):
    db.user_online(current_user.get_id(), set = True)
    emit('receive friendlist', db.user_friendlist(current_user.get_id()))
    emit('receive friendgrouplist', db.user_friendgroup(current_user.get_id()))
    emit('first response', {'data': 'Connected'})


@socketio.on('refresh friendgrouplist', namespace = '/message')
def refresh_friendlist(msg):
    db.user_online(current_user.get_id(), set = True)
    emit('receive friendgrouplist', db.user_friendgroup(current_user.get_id()))

@socketio.on('refresh friendlist', namespace = '/message')
def refresh_friendlist(msg):
    db.user_online(current_user.get_id(), set = True)
    emit('receive friendlist', db.user_friendlist(current_user.get_id()))


@socketio.on('send message', namespace='/message')
def sender_send_message(data):
    db.user_online(current_user.get_id(), set = True)
    # print data['message']
    data['message'] = data['message'].replace(' ', u'\xa0')
    # print data['message']
    message = {'message': data['message'], 'time': time.strftime("%b %e %Y %T", time.localtime(time.time()))}
    sender = current_user.get_id()
    receiver = data['receiver']
    app.logger.debug('user {} send message to {}'.format(sender, receiver))
    db.message_sent(sender = sender, receiver = receiver, message = message)
    if db.user_online(receiver) == 'True':
        emit('receive message', {'sender': sender, 'message': message}, room = receiver)
        db.message_received(sender = sender, receiver = receiver, message = message)
    else:
        db.message_processing_wating(sender = sender, receiver = receiver, message = message)
    message['self'] = True
    emit('receive message', {'sender': receiver, 'message': message}, room = sender)
    # send_message(sender = current_user.get_id(), receiver = data['receiver'], message = message)


@socketio.on('receive wating message', namespace = '/message')
def receiver_receive_wating_message():
    db.user_online(current_user.get_id(), set = True)
    while True:
        message = db.get_wating_message(current_user.get_id())
        # print message
        # print 'reach0'
        if message is None:
            print 'reachnone'
            break
        # send_message(sender = message['sender'], receiver = current_user.get_id(), message = message['message'])
        # print 'reach01'
        # print type(message)
        # # print json.loads(message)
        message = json.loads(message)
        # print message
        # print 'reach02'
        sender = message['sender']
        # print 'reach03'
        receiver = current_user.get_id()
        # print 'reach04'
        message = message['message']
        # print 'reach05'
        if db.user_online(receiver) == 'True':
            # print 'reach3'
            emit('receive message', {'sender': sender, 'message': message}, room = receiver)
            db.message_received(sender = sender, receiver = receiver, message = message)
        else:
            # print 'reach4'
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
