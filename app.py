from flask import Flask, render_template, abort, request
from flask import redirect, url_for
from flask_httpauth import HTTPDigestAuth
from game.models import Hardware, Games
from game.database import db_session
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
@app.route('/login')
@auth.login_required
def login():
    if auth.username() == "tenmaendou":
        return redirect(url_for('manage'))
    else:
        return render_template("login.html", username=auth.username())


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
    hard_contents = Hardware.query.all()
    soft_contents = Games.query.all()
    hard_contents = Hardware.query.all()
    return render_template(
                "manage.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
            )


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
    return "ok"  # redirect(url_for('manage'))
    """
    bf4 = Games(title='Battlefield3')
    ps3 = session.query(Hardware).filter_by(id=3).one()
    ps4 = session.query(Hardware).filter_by(id=4).one()
    bf4.hardwares.extend([ps3, ps4])
    session.add(bf4)
    session.commit()
    return "ok"
    """


if __name__ == "__main__":
    app.run(debug=True)
