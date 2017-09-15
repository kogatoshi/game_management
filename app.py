from flask import Flask, render_template, abort, request
from flask import redirect, url_for, flash, session, g
from flask_httpauth import HTTPDigestAuth
from functools import wraps
from game import database, models
import logging
import os
import sys


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
auth = HTTPDigestAuth()

db_session = database.db_session()


def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_view


@app.before_request
def load_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = models.User.query.get(session['user_id'])


# 最初のページ
@app.route('/')
def home():
    hard_contents = models.Hardware.query.all()
    soft_contents = models.Games.query.all()
    return render_template(
                "index.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
                username=auth.username()
            )


# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, authenticated = models.User.authenticate(
                                db_session.query,
                                request.form['email'],
                                request.form['password']
                            )
        if authenticated:
            session['user_id'] = user.id
            if user.username == 'tenmaendou':
                return redirect(url_for('manage'))
            else:
                flash('You were logged in')
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('home'))


# ソフト・ハードの一覧
@app.route("/game")
@login_required
def game():
    hard_contents = models.Hardware.query.all()
    soft_contents = models.Games.query.all()
    return render_template(
                "game_list.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
                username=auth.username()
            )


"""
@app.route("/signup_conf", methods=['POST'])
def signup_conf():
    new_username = request.form['new_username']
    email = request.form['email']
    password = request.form['password']
    return render_template(
                'signup_conf.html',
                new_username=new_username,
                email=email,
                password=password,
            )
"""


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/adduser", methods=['POST'])
@login_required
def adduser():
    if request.method == 'POST':
        user = models.User(
                username=request.form['new_username'],
                address=request.form['email'],
                password=request.form['password']
            )
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


# 詳細ページ
@app.route("/<name>", methods=["GET"])
def show_content(name):
    content = models.Hardware.query.filter_by(name=name).first()
    if content is None:
        abort(404)
    return render_template("show_content.html", content=content)


# 管理ページ
@app.route("/manage")
@login_required
def manage():
    hard_contents = db_session.query(models.Hardware).all()
    soft_contents = db_session.query(models.Games).all()
    return render_template(
                "manage.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
            )


# ソフトをデータベースに追加
@app.route("/addsoft", methods=["POST"])
@login_required
def addsoft():
    # テキストボックスからソフトの名前を取得
    title = request.form["softName"]
    # チェックボックスからハードウェアのリストを取得
    hardnumbers = request.form.getlist("hardNumbers")
    if title and hardnumbers:
        game = models.Games(title=title)
        hards = []
        for hard in hardnumbers:
            name = db_session.query(models.Hardware).filter_by(id=hard).one()
            hards.append(name)
        game.hardwares.extend(hards)

        db_session.add(game)
        db_session.commit()
        flash('%sを追加しました！' % (title))
    else:
        if title:
            flash('ハードを選択してください')
        if hardnumbers:
            flash('ソフト名を入力してください')
    return redirect(url_for('manage'))


@app.route("/addhard", methods=["POST"])
@login_required
def addhard():
    name = request.form["hardName"]
    if name:
        new_hard = models.Hardware(name=name)
        db_session.add(new_hard)
        db_session.commit()
    else:
        flash('入力してください')
    return redirect(url_for('manage'))


@app.route("/deletesoft", methods=["POST"])
@login_required
def deletesoft():
    delsoft_id = list(request.form.keys())[0]
    delsoft_title = \
        db_session.query(models.Games).filter_by(id=delsoft_id).one()
    # delete_soft = models.Games(title=delsoft_title, id=delsoft_id)
    db_session.delete(delsoft_title)
    db_session.commit()
    flash('削除しました')
    return redirect(url_for('manage'))


if __name__ == "__main__":
    app.run(debug=True)
