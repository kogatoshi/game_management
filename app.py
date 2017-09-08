from flask import Flask, render_template, abort, request
from flask import session, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from game.models import Hardware, Games
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
auth = HTTPBasicAuth()

users = {"john": "hello", "susan": "bye"}


@app.before_request
def before_request():
    if session.get('username') is not None:
        return
    if request.path == '/login':
        return
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and _is_account_valid():
        session['username'] = request.form['username']
        return redirect(url_for('game'))
    return render_template('login.html')


def _is_account_valid():
    username = request.form.get('username')
    if username == 'admin':
        return True
    return False


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/")
@auth.login_required
def game():
    hard_contents = Hardware.query.all()
    soft_contents = Games.query.all()
    return render_template(
            "index.html",
            hard_contents=hard_contents,
            soft_contents=soft_contents
        )


@app.route("/<name>", methods=["GET"])
def show_content(name):
    content = Hardware.query.filter_by(name=name).first()
    if content is None:
        abort(404)
    return render_template("show_content.html", content=content)


if __name__ == "__main__":
    app.run(debug=True)
