from flask import render_template, Blueprint
from flask_login import current_user, login_required
from model import db
# from account import account
# # from message import message
# from user import user, User
# from flask_socketio import SocketIO, emit
# from flask_login import LoginManager
#
#
# app = Flask(__name__)
#
#
#
#
#
#
# if __name__ == "__main__":
#     app.debug = True
#     socketio.init_app(app)
#     socketio.run(app, host = '127.0.0.1', port = 5000)

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
@login_required
def index():
    # return render_template('socket.html')
    return render_template('main.html', id=current_user.get_id(), db=db)