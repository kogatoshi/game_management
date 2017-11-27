from flask import Flask, render_template, abort, request
from flask import redirect, url_for, flash, session, g
from flask_httpauth import HTTPDigestAuth
from flask_wtf.csrf import CSRFProtect
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
csrf = CSRFProtect(app)

db_session = database.db_session()


def login_required(f):
    @wraps(f)
    def decorated_view(*args, **kwargs):
        if g.user is None:
            flash("ログインしてください")
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


@app.context_processor
def utility_processor():
    def user_info():
        user_id = session['user_id']
        user = db_session.query(models.User).filter_by(id=user_id)
        return user
    return dict(user_info=user_info)


@app.route('/')
def top():
    return render_template("index.html")


@app.route('/home')
@login_required
def home():
    hard_contents = db_session.query(models.Hardware).all()
    soft_contents = db_session.query(models.Games).all()
    possess_hards_id = db_session.query(models.user_hard_table).\
        filter_by(user_id=session['user_id'])
    possess_softs_id = db_session.query(models.user_game_table).\
        filter_by(user_id=session['user_id'])
    possess_hards = []
    possess_softs = []
    for ph in possess_hards_id:
        poss = db_session.query(models.Hardware).filter_by(id=ph[1]).one().id
        possess_hards.append(poss)
    for ps in possess_softs_id:
        poss = db_session.query(models.Games).filter_by(id=ps[1]).one().id
        possess_softs.append(poss)
    return render_template(
                "home.html",
                hard_contents=hard_contents,
                soft_contents=soft_contents,
                possess_hards=possess_hards,
                possess_softs=possess_softs,
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
            session['username'] = user.username
            if user.username == 'tenmaendou':
                return redirect(url_for('manage'))
            else:
                flash('You were logged in')
                return render_template(
                            'index.html',
                            level=user.level,
                        )
        else:
            flash('Invalid email or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    flash('You were logged out')
    return redirect(url_for('login'))


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


# 所持しているハードウェアを追加
@app.route("/possess_hard", methods=['POST'])
def possess_hard():
    hard_id = request.form['hard_id']
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    poshard = db_session.query(models.Hardware).filter_by(id=hard_id).one()
    user.hardwares.append(poshard)
    db_session.add(user)
    db_session.commit()
    return redirect(url_for('home'))


# 所持しているソフトを追加
@app.route("/possess_soft", methods=['POST'])
def possess_soft():
    soft_id = request.form['soft_id']
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    possoft = db_session.query(models.Games).filter_by(id=soft_id).one()
    user.games.append(possoft)
    db_session.add(user)
    db_session.commit()
    return redirect(url_for('home'))


# 所持していたソフトを削除
@app.route("/del_possess_soft", methods=['POST'])
def del_possess_soft():
    game_id = request.form['soft_id']
    user_id = session['user_id']
    delposgame = db_session.query(models.Games).filter_by(id=game_id).one()
    user = db_session.query(models.User).filter_by(id=user_id).one()
    user.games.remove(delposgame)
    db_session.commit()
    return redirect(url_for('mypage'))


# 所持していたハードを削除
@app.route("/del_possess_hard", methods=['POST'])
def del_possess_hard():
    hard_id = request.form['hard_id']
    user_id = session['user_id']
    delposhard = db_session.query(models.Hardware).filter_by(id=hard_id).one()
    user = db_session.query(models.User).filter_by(id=user_id).one()
    user.games.remove(delposhard)
    db_session.commit()
    return redirect(url_for('mypage'))


# マイページ
@app.route("/mypage")
def mypage():
    possess_hards_id = db_session.query(models.user_hard_table).\
        filter_by(user_id=session['user_id'])
    possess_softs_id = db_session.query(models.user_game_table).\
        filter_by(user_id=session['user_id'])
    possess_hards = []
    possess_softs = []
    for ph in possess_hards_id:
        poss = db_session.query(models.Hardware).filter_by(id=ph[1]).one().name
        possess_hards.append(poss)
    for ps in possess_softs_id:
        poss = db_session.query(models.Games).filter_by(id=ps[1]).one().title
        possess_softs.append(poss)
    return render_template(
                'mypage.html',
                possess_hards=possess_hards,
                possess_softs=possess_softs,
            )


# 詳細ページ
@app.route("/hardware/<name>", methods=["GET"])
@login_required
def show_content_hard(name):
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    hard = db_session.query(models.Hardware).filter_by(name=name).one()
    done = False
    if hard is None:
        abort(404)
    for hr in hard.review:
        if user == hr.users:
            done = True
    return render_template(
                "show_content_hard.html",
                hard=hard,
                hardreview=hard.review,
                done=done,
            )


@app.route("/software/<title>", methods=["GET"])
@login_required
def show_content_soft(title):
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    soft = db_session.query(models.Games).filter_by(title=title).one()
    done = False
    if soft is None:
        abort(404)
    for sr in soft.review:
        if user == sr.users:
            done = True
    return render_template(
                "show_content_soft.html",
                soft=soft,
                softreview=soft.review,
                done=done,
            )


# 管理ページ
@app.route("/manage")
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
        for hn in hardnumbers:
            hard = db_session.query(models.Hardware).filter_by(id=hn).one()
            hards.append(hard)
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
    delsoft_id = list(request.form.keys())[1]
    delsoft_title = \
        db_session.query(models.Games).filter_by(id=delsoft_id).one()
    # delete_soft = models.Games(title=delsoft_title, id=delsoft_id)
    db_session.delete(delsoft_title)
    db_session.commit()
    flash('削除しました')
    return redirect(url_for('manage'))


@app.route("/hardreview", methods=["POST"])
@login_required
def hardreview():
    # ユーザー情報取得
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    # if db_session.query(models.Hardreview).filter_by(users=user)
    hard_name = request.form["hardname"]
    hard = db_session.query(models.Hardware).filter_by(name=hard_name).one()
    star = request.form["HardReviewStar"]
    comment = request.form["text"]
    hardreview = models.Hardreview(text=comment, star=star, users=user)
    hard.review.append(hardreview)
    db_session.commit()
    return redirect("/hardware/%s" % hard_name)


@app.route("/softreview", methods=["POST"])
@login_required
def softreview():
    # ユーザー情報取得
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    # if db_session.query(models.Hardreview).filter_by(users=user)
    soft_name = request.form["softname"]
    soft = db_session.query(models.Games).filter_by(title=soft_name).one()
    star = request.form["softReviewStar"]
    comment = request.form["text"]
    softreview = models.Softreview(text=comment, star=star, users=user)
    soft.review.append(softreview)
    db_session.commit()
    return redirect("/software/%s" % soft_name)


@app.route('/addchat', methods=["POST"])
@login_required
def addchat():
    user_id = session['user_id']
    user = db_session.query(models.User).filter_by(id=user_id).one()
    chat_text = request.form["chatText"]
    addchat = models.Chat(text=chat_text, user=user)
    db_session.add(addchat)
    db_session.commit()
    chat = db_session.query(models.Chat).all()
    return render_template("chat.html", chat=chat)


@app.route('/chat')
@login_required
def chat():
    chat = db_session.query(models.Chat).order_by(asc(models.Chat.datetime))
    return render_template("chat.html", chat=chat)


if __name__ == "__main__":
    app.run(debug=True,
            host=os.getenv('IP', '127.0.0.1'),
            port=int(os.getenv('PORT', 1919))
            )
