from flask import Flask, render_template, abort, request
from flask import redirect, url_for
from flask_httpauth import HTTPDigestAuth
from game.models import Hardware, Games, User
from game.database import db_session, engine
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
auth = HTTPDigestAuth()

session = db_session()

users = {"john": "hello", "susan": "bye", "tenmaendou": "tenma129"}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


# 最初のページ
@app.route('/')
def home():
    return render_template("index.html")


# ログイン
@app.route('/login', methods=['POST'])
@auth.login_required
def login():
    users = session.query(User).all()
    return "ok"


# ソフト・ハードの一覧
@app.route("/game")
def game():
    hard_contents = Hardware.query.all()
    soft_contents = Games.query.all()
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
            )


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/adduser", methods=['POST'])
def adduser():
    new_username = signup_conf.new_username
    email = signup_conf.email
    password = signup_conf.password
    engine.execute(
        'insert into users values \
        (0, "%s", "%s", "%s")' % (new_username, email, password)
    )
    return redirect(url_for('login'))


# 詳細ページ
@app.route("/<name>", methods=["GET"])
def show_content(name):
    content = Hardware.query.filter_by(name=name).first()
    if content is None:
        abort(404)
    return render_template("show_content.html", content=content)


# 管理ページ
@app.route("/manage")
def manage():
    hard_contents = session.query(Hardware).all()
    soft_contents = session.query(Games).all()
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
    game = Games(title=title)
    hards = []
    for hard in hardnumbers:
        name = session.query(Hardware).filter_by(id=hard).one()
        hards.append(name)
    game.hardwares.extend(hards)

    session.add(game)
    session.commit()
    return redirect(url_for('manage'))


@app.route("/addhard", methods=["POST"])
def addhard():
    name = request.form["hardName"]
    engine.execute('insert into hardware values (0, "%s")' % (name))
    return redirect(url_for('manage'))


if __name__ == "__main__":
    app.run(debug=True)
