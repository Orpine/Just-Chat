from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_log import Logging
import logging
socketio = SocketIO()


def create_app(debug=False):
    app = Flask(__name__, template_folder = 'templates')
    app.debug = debug
    app.config['SECRET_KEY'] = 'burstlink!'
    app.config['FLASK_LOG_LEVEL'] = 'DEBUG'
    flask_log = Logging(app)
    app.jinja_env.variable_start_string = '[['
    app.jinja_env.variable_end_string = ']]'
    from main import main
    from account import account
    from message import message
    from user import user, User
    app.register_blueprint(main, url_prefix='/main')
    app.register_blueprint(account, url_prefix='/account')
    app.register_blueprint(message, url_prefix='/message')
    app.register_blueprint(user, url_prefix='/user')

    socketio.init_app(app)
    return app
