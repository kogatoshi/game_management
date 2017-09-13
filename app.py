from flask import Flask, render_template, abort, request
from flask import redirect, url_for, flash, session
from flask_httpauth import HTTPDigestAuth
from game import database, models
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
auth = HTTPDigestAuth()

db_session = database.db_session()

"""
@auth.get_password
def get_pw(username):
    users = session.query(User).all()
    if username in users:
        return users.get(username)
    return None
"""


# 最初のページ
@app.route('/')
def home():
    return render_template("index.html")


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
            flash('You were logged in')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('login'))


# ソフト・ハードの一覧
@app.route("/game")
def game():
    hard_contents = models.Hardware.query.all()
    soft_contents = models.Games.query.all()
    return render_template(
                "game_list.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
                username=auth.username()
            )


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


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/adduser", methods=['POST'])
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
def manage():
    hard_contents = db_session.query(models.Hardware).all()
    soft_contents = db_session.query(models.Games).all()
    if hard_contents:
        return render_template(
                    "manage.html",
                    hard_contents=hard_contents,
                    soft_contents=soft_contents,
                )
    else:
        return "ハードを登録してください"


# ソフトをデータベースに追加
@app.route("/addsoft", methods=["POST"])
def addsoft():
    # テキストボックスからソフトの名前を取得
    title = request.form["softName"]
    # チェックボックスからハードウェアのリストを取得
    hardnumbers = request.form.getlist("hardNumbers")
    game = models.Games(title=title)
    hards = []
    for hard in hardnumbers:
        name = db_session.query(models.Hardware).filter_by(id=hard).one()
        hards.append(name)
    game.hardwares.extend(hards)

    db_session.add(game)
    db_session.commit()
    return redirect(url_for('manage'))


@app.route("/addhard", methods=["POST"])
def addhard():
    name = request.form["hardName"]
    database.engine.execute('insert into hardware values (0, "%s")' % (name))
    return redirect(url_for('manage'))


if __name__ == "__main__":
    app.run(debug=True)
