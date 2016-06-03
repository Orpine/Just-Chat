from chat_server import create_app, socketio
from chat_server.user import User
from flask_login import LoginManager
from flask import render_template, redirect, url_for
from flask_login import current_user


app = create_app(debug=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/'


@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User(id = user_id)


@app.route('/')
def hello_world():
    if current_user.is_authenticated:
        return redirect('/main')
    else:
        return redirect('/account')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
